from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from langchain_core.documents import Document
import requests
import os
import traceback

app = Flask(__name__)
CORS(app)  # Habilitar CORS para permitir peticiones del frontend

# Ruta base de datos vectorial y documentos
DATA_PATH = "data/docs"
INDEX_PATH = "data/nicsp_index"

# Embeddings gratuitos
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Construir o cargar índice
if not os.path.exists(INDEX_PATH):
    print("Generando base de conocimiento FAISS...")
    docs = []

    def read_text_file(path):
        """Leer un archivo y devolver texto. Soporta .txt, .md, .csv, .json, .pdf y .docx (si está python-docx).
        Intenta varias codificaciones antes de fallar.
        """
        _, ext = os.path.splitext(path)
        ext = ext.lower()

        # PDF (usa PyMuPDF / fitz)
        if ext == ".pdf":
            try:
                import fitz
                doc = fitz.open(path)
                text = []
                for page in doc:
                    text.append(page.get_text())
                return "\n".join(text)
            except Exception as e:
                print(f"No se pudo leer PDF {path}: {e}")
                return ""

        # DOCX (opcional)
        if ext == ".docx":
            try:
                import docx
                d = docx.Document(path)
                return "\n".join([p.text for p in d.paragraphs])
            except Exception as e:
                print(f"No se pudo leer DOCX {path} (instala python-docx para soporte): {e}")
                return ""

        # Text-like files: probar múltiples codificaciones
        if ext in (".txt", ".md", ".csv", ".json"):
            for enc in ("utf-8", "latin-1", "cp1252"):
                try:
                    with open(path, encoding=enc) as f:
                        return f.read()
                except Exception:
                    continue
            print(f"No se pudo decodificar {path} con utf-8/latin-1/cp1252; omitiendo.")
            return ""

        # Intento genérico: leer como binario y decodificar
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

    for file in os.listdir(DATA_PATH):
        file_path = os.path.join(DATA_PATH, file)
        if os.path.isdir(file_path):
            continue

        text = read_text_file(file_path)
        if not text or not text.strip():
            print(f"Omitiendo archivo vacío o no legible: {file}")
            continue

        chunks = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100).split_text(text)
        for chunk in chunks:
            docs.append(Document(page_content=chunk, metadata={"source": file}))

    db = FAISS.from_documents(docs, embeddings)
    db.save_local(INDEX_PATH)
else:
    print("Cargando índice FAISS existente...")
    db = FAISS.load_local(INDEX_PATH, embeddings, allow_dangerous_deserialization=True)

# Modelo local de IA (gemma:2b - balance perfecto calidad/velocidad para Ryzen 5 5500U)
# Ryzen 5 5500U con 16GB RAM puede manejar modelos medianos sin problema
MODEL_NAME = "gemma:2b"
OLLAMA_URL = "http://localhost:11434"


def call_ollama_api(prompt: str) -> str:
    """Llama a la API HTTP de Ollama para generar una respuesta.
    
    Retorna el texto de la respuesta.
    """
    try:
        # Parámetros optimizados para Ryzen 5 5500U (16GB RAM, 6 cores)
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_ctx": 2048,        # Contexto normal (mejor comprensión)
                    "num_gpu": 1,           # Usar iGPU Vega (2GB) para acelerar
                    "num_thread": 6,        # Usar los 6 cores de la Ryzen 5
                    "num_batch": 512,       # Batch más grande = más rápido
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
            # Método común en FAISS wrapper
            docs = db.similarity_search(message, k=4)
        except Exception:
            # fallback a otro nombre de método
            try:
                docs_with_score = db.similarity_search_with_score(message, k=4)
                docs = [d for d, s in docs_with_score]
            except Exception:
                docs = []

        # Construir contexto a partir de los documentos recuperados
        if docs:
            context = "\n\n".join([
                f"Fuente: {getattr(d, 'metadata', {}).get('source', '')}\n{getattr(d, 'page_content', getattr(d, 'text', ''))}"
                for d in docs
            ])
        else:
            context = ""

        prompt = (
            "Eres un asistente experto en NICSP. Responde la pregunta de forma CONCISA y DIRECTA usando SOLO la información del contexto proporcionado.\n"
            "Si la pregunta es un saludo simple (hola, cómo estás, etc), responde brevemente de forma amigable.\n"
            "Si la pregunta no está relacionada con el contexto, di: 'No tengo información sobre eso en mis documentos NICSP.'\n\n"
            f"Contexto NICSP:\n{context}\n\n"
            f"Pregunta: {message}\n\n"
            "Respuesta (máximo 3 párrafos):"
        )

        answer = call_ollama_api(prompt)
        return jsonify({"response": answer})
    except Exception as e:
        return jsonify({"error": f"Error interno: {e}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
