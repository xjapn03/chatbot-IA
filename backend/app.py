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
CORS(app)

DATA_PATH = "data/docs"
INDEX_PATH = "data/nicsp_index"

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

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
        print(f"No se pudo leer DOCX {path}: {e}")
        return ""

def read_text_like(path):
    for enc in ("utf-8", "latin-1", "cp1252"):
        try:
            with open(path, encoding=enc) as f:
                return f.read()
        except Exception:
            continue
    print(f"No se pudo decodificar {path}; omitiendo.")
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
        return text.strip()
    
    def read_text_file(path):
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
        if not text:
            print(f"Omitiendo archivo vacío: {file}")
            continue
        
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=750,             # Tamaño óptimo para listas largas
            chunk_overlap=120,          # Mantener overlap proporcional
            separators=["\n\n", "\n", ". ", ".", " "]
        )
        chunks = splitter.split_text(text)
        for chunk in chunks:
            docs.append(Document(page_content=chunk, metadata={"source": file}))
    
    print(f"✓ Total documentos cargados: {len(docs)}")
    db = FAISS.from_documents(docs, embeddings)
    db.save_local(INDEX_PATH)
else:
    print("Cargando índice FAISS existente...")
    db = FAISS.load_local(INDEX_PATH, embeddings, allow_dangerous_deserialization=True)

MODEL_NAME = "llama3.2:3b"
OLLAMA_URL = "http://98.95.116.221:11434"


def call_ollama_api(prompt: str) -> str:
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_ctx": 1280,        # Aumentar ligeramente para contextos más largos
                    "num_thread": 2,
                    "num_batch": 64,
                    "temperature": 0.3,
                    "top_p": 0.85,
                    "top_k": 30,
                    "repeat_penalty": 1.15,
                    "num_predict": 220      # Aumentar un poco para respuestas más completas
                }
            },
            timeout=120                     # 2 minutos para evitar timeouts
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("response", "").strip()
        else:
            error_msg = f"Error {response.status_code}"
            print(f"[ERROR] Ollama: {error_msg}")
            return f"Error al llamar a Ollama: {error_msg}"
    
    except Exception as e:
        print(f"[ERROR] {e}")
        return f"Error: {str(e)}"


def clean_and_validate_response(response: str, context: str) -> str:
    suspicious = ["remetente", "confirmante", "según mi conocimiento"]
    response_lower = response.lower()
    context_lower = context.lower()
    
    for term in suspicious:
        if term in response_lower and term not in context_lower:
            return "No tengo información suficiente en mis documentos NICSP."
    
    response = response.strip()
    
    #  Permitir respuestas de "no sé" ANTES de validar longitud
    no_info_phrases = ["no encuentro", "no tengo", "no está", "no se encuentra", "no hay información"]
    if any(phrase in response_lower for phrase in no_info_phrases):
        return response
    
    #  Reducir umbral mínimo a 20 caracteres
    if len(response) < 20:
        return "No encuentro información específica sobre eso en los documentos."
    
    return response


@app.post("/chat")
def chat():
    message = request.json.get("message", "")
    if not message:
        return jsonify({"error": "No message provided"}), 400
    
    try:
        docs = db.similarity_search(message, k=8)  # Recuperar más documentos iniciales
        
        if docs:
            query_embedding = embeddings.embed_query(message)
            doc_embeddings = embeddings.embed_documents([d.page_content for d in docs])
            scores = cosine_similarity([query_embedding], doc_embeddings)[0]
            ranked = sorted(zip(scores, docs), reverse=True, key=lambda x: x[0])
            
            # Tomar TOP 4 mejores después de re-ranking
            top_docs = [doc for _, doc in ranked[:4]]
            
            context_parts = []
            for doc in top_docs:
                source = doc.metadata.get('source', '')
                content = doc.page_content.strip()
                context_parts.append(f"[{source}]\n{content}")
            
            context = "\n\n".join(context_parts)
            
            # Límite de contexto aumentado para permitir respuestas más completas
            if len(context) > 1600:
                context = context[:1600] + "\n[...]"
        else:
            context = ""
        
        print(f"\n{'='*60}")
        print(f"PREGUNTA: {message}")
        print(f"DOCS: {len(docs)}")
        print(f"CONTEXTO ({len(context)} chars):\n{context}")
        print(f"{'='*60}\n")
        
        prompt = f"""Contexto de NICSP:
{context}

Pregunta: {message}

Instrucciones: Responde usando SOLO el contexto anterior. Si no hay información suficiente, di "No encuentro esa información específica". Máximo 4 oraciones claras.

Respuesta:"""
        
        answer = call_ollama_api(prompt)
        answer = clean_and_validate_response(answer, context)
        
        print(f"[RESPUESTA]: {answer}\n")
        
        return jsonify({"response": answer})
    
    except Exception as e:
        print("[ERROR]:", traceback.format_exc())
        return jsonify({"error": f"Error interno: {e}"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)