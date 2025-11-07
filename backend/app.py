from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import requests
import os
import traceback
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

app = Flask(__name__)
CORS(app)  # Habilitar CORS para permitir peticiones del frontend

# Ruta base de datos vectorial y documentos
DATA_PATH = "data/docs"
INDEX_PATH = "data/nicsp_index"

# Embeddings gratuitos
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

# --- Funciones auxiliares para lectura de archivos ---
def read_pdf(path):
    try:
        import fitz
        doc = fitz.open(path)
        return "\n".join(page.get_text() for page in doc)
    except Exception as e:
        print(f"No se pudo leer PDF {path}: {e}")
        return ""

def read_docx(path):
    try:
        import docx
        d = docx.Document(path)
        return "\n".join(p.text for p in d.paragraphs)
    except Exception as e:
        print(f"No se pudo leer DOCX {path} (instala python-docx para soporte): {e}")
        return ""

def read_text_like(path):
    for enc in ("utf-8", "latin-1", "cp1252"):
        try:
            with open(path, encoding=enc) as f:
                return f.read()
        except Exception:
            continue
    print(f"No se pudo decodificar {path} con utf-8/latin-1/cp1252; omitiendo.")
    return ""

def read_generic(path):
    try:
        with open(path, "rb") as f:
            data = f.read()
        for enc in ("utf-8", "latin-1", "cp1252"):
            try:
                return data.decode(enc)
            except Exception:
                continue
    except Exception as e:
        print(f"No se pudo leer {path}: {e}")
    return ""

# Construir o cargar índice
if not os.path.exists(INDEX_PATH):
    print("Generando base de conocimiento FAISS...")
    docs = []

    import re
    def clean_text(text):
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        return text

    def read_text_file(path):
        """Lee un archivo y devuelve su texto según la extensión."""
        _, ext = os.path.splitext(path)
        ext = ext.lower()
        if ext == ".pdf":
            return read_pdf(path)
        if ext == ".docx":
            return read_docx(path)
        if ext in (".txt", ".md", ".csv", ".json"):
            return read_text_like(path)
        return read_generic(path)

    for file in os.listdir(DATA_PATH):
        file_path = os.path.join(DATA_PATH, file)
        if os.path.isdir(file_path):
            continue

        text = clean_text(read_text_file(file_path))
        if not text or not text.strip():
            print(f"Omitiendo archivo vacío o no legible: {file}")
            continue

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=100,
            separators=["\n\n", "\n", ".", " ", ""]
        )
        chunks = splitter.split_text(text)
        for chunk in chunks:
            docs.append(Document(page_content=chunk, metadata={"source": file}))
        # Fin del for: ahora creamos el índice FAISS
    db = FAISS.from_documents(docs, embeddings)
    db.save_local(INDEX_PATH)
else:
    print("Cargando índice FAISS existente...")
    db = FAISS.load_local(INDEX_PATH, embeddings, allow_dangerous_deserialization=True)

MODEL_NAME = "gemma:2b"
#instancia en AWS
OLLAMA_URL = "http://98.95.116.221:11434"


def call_ollama_api(prompt: str) -> str:
    """Llama a la API HTTP de Ollama para generar una respuesta.
    
    Retorna el texto de la respuesta.
    """
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_ctx": 512,         # Contexto mínimo para pruebas
                    "num_thread": 2,        # Igual al número de vCPU
                    "num_batch": 32,        # Batch mínimo para pruebas
                    "temperature": 0.7,     # Respuestas más coherentes
                    "top_p": 0.9,
                    "top_k": 40
                }
            },
            timeout=60  # Reducir timeout - tu PC es rápido
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("response", "").strip()
        elif response.status_code == 500 and "memory" in response.text.lower():
            # Si falla por memoria, sugerir modelo más ligero
            print("[ERROR] El modelo necesita más RAM. Considera usar tinyllama o gemma:2b")
            return "⚠️ El modelo necesita más RAM. Por favor:\n1. Cierra otras aplicaciones\n2. O cambia a un modelo más ligero en backend/app.py:\n   MODEL_NAME = 'tinyllama' o 'gemma:2b'\nLuego reinicia el servidor backend."
        else:
            error_msg = f"Error {response.status_code}: {response.text}"
            print(f"[ERROR] Ollama API: {error_msg}")
            return f"Error al llamar a Ollama API: {error_msg}"
            
    except requests.exceptions.ConnectionError:
        return "No se pudo conectar a Ollama. Asegúrate de que Ollama esté corriendo."
    except requests.exceptions.Timeout:
        return "La consulta tardó demasiado tiempo. Intenta con una pregunta más corta."
    except Exception as e:
        print(f"[ERROR] Excepción al llamar a Ollama: {e}")
        return f"Error al llamar al modelo: {str(e)}"

@app.post("/chat")
def chat():
    message = request.json.get("message", "")
    if not message:
        return jsonify({"error": "No message provided"}), 400
    
    try:
        # Recuperar los documentos más relevantes
        docs = []
        try:
            docs = db.similarity_search(message, k=6)
        except Exception:
            try:
                docs_with_score = db.similarity_search_with_score(message, k=6)
                docs = [d for d, s in docs_with_score]
            except Exception:
                docs = []

        # Re-ranking local
        if docs:
            query_embedding = embeddings.embed_query(message)
            doc_embeddings = embeddings.embed_documents([d.page_content for d in docs])
            scores = cosine_similarity([query_embedding], doc_embeddings)[0]
            ranked = sorted(zip(scores, docs), reverse=True, key=lambda x: x[0])
            docs = [doc for _, doc in ranked[:3]]

        # Construir contexto a partir de los documentos recuperados
        if docs:
            context = "\n\n".join([
                f"Fuente: {getattr(d, 'metadata', {}).get('source', '')}\n{getattr(d, 'page_content', getattr(d, 'text', ''))}"
                for d in docs
            ])
        else:
            context = ""

        prompt = (
            "Eres un experto en las Normas Internacionales de Contabilidad del Sector Público (NICSP).\n"
            "Responde SOLO usando la información del contexto.\n"
            "Si no hay información suficiente, responde: 'No tengo información sobre eso en mis documentos NICSP.'\n"
            "Evita suposiciones o información inventada.\n\n"
            f"Contexto relevante:\n{context}\n\n"
            f"Pregunta del usuario: {message}\n\n"
            "Respuesta (máximo 3 párrafos, clara y precisa):"
        )

        answer = call_ollama_api(prompt)
        return jsonify({"response": answer})
    except Exception as e:
        print("[ERROR chat]:", traceback.format_exc())
        return jsonify({"error": f"Error interno: {e}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
