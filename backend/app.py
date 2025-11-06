from flask import Flask, request, jsonify
from langchain.vectorstores import FAISS
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.llms import Ollama
from langchain.chains import RetrievalQA
from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document
import os

app = Flask(__name__)

# Ruta base de datos vectorial y documentos
DATA_PATH = "data/docs"
INDEX_PATH = "data/nicsp_index"

# Embeddings gratuitos
embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

# Construir o cargar índice
if not os.path.exists(INDEX_PATH):
    print("Generando base de conocimiento FAISS...")
    docs = []
    for file in os.listdir(DATA_PATH):
        text = open(os.path.join(DATA_PATH, file), encoding="utf-8").read()
        chunks = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100).split_text(text)
        for chunk in chunks:
            docs.append(Document(page_content=chunk, metadata={"source": file}))
    db = FAISS.from_documents(docs, embeddings)
    db.save_local(INDEX_PATH)
else:
    print("Cargando índice FAISS existente...")
    db = FAISS.load_local(INDEX_PATH, embeddings, allow_dangerous_deserialization=True)

# Modelo local de IA gratuito (phi3)
llm = Ollama(model="phi3")
qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=db.as_retriever())

@app.post("/chat")
def chat():
    message = request.json["message"]
    result = qa_chain({"query": message})
    return jsonify({"reply": result["result"]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
