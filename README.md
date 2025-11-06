# Chatbot NICSP - Asistente de Normas Internacionales

Chatbot inteligente para consultas sobre **Normas Internacionales de Contabilidad del Sector Público (NICSP)** usando IA local con Ollama y RAG (Retrieval-Augmented Generation).

## Descripción

Este proyecto es un MVP de chatbot que combina:
- **Backend**: Python con Flask, LangChain, FAISS y Ollama
- **Frontend**: Next.js 16 con React y Tailwind CSS
- **IA**: Modelos locales de Ollama (Llama3, Mistral, Phi3)
- **Base de conocimiento**: Documentos NICSP procesados con embeddings

## Arquitectura

```
chatbot-IA/
├── backend/          # API Flask + LangChain
│   ├── app.py        # Servidor principal
│   ├── requirements.txt
│   └── data/
│       ├── docs/     # Documentos NICSP (txt, pdf, etc.)
│       └── nicsp_index/  # Índice vectorial FAISS (generado automáticamente)
│
└── frontend/         # Aplicación Next.js
    ├── app/
    │   ├── Chatbot.jsx   # Componente del chat
    │   ├── page.tsx      # Página principal
    │   └── layout.tsx
    └── package.json
```

## Requisitos Previos

### 1. Ollama
Debes tener Ollama instalado y corriendo:

**Instalación:**
- Descarga desde: https://ollama.ai
- Instala y verifica:
```bash
ollama --version
```

**Descargar modelo (elige uno):**
```bash
# Opción 1: Llama3 (recomendado, ~4.7GB)
ollama pull llama3

# Opción 2: Mistral (~4.1GB)
ollama pull mistral

# Opción 3: Phi3 (más ligero, ~2.3GB)
ollama pull phi3
```

**Verificar que el modelo está corriendo:**
```bash
ollama list
```

### 2. Python 3.8+
```bash
python --version
```

### 3. Node.js 18+
```bash
node --version
npm --version
```

## Instalación

### Backend

1. **Navega a la carpeta backend:**
```bash
cd backend
```

2. **Crea un entorno virtual (recomendado):**
```bash
python -m venv venv
```

3. **Activa el entorno virtual:**
```bash
# Windows PowerShell
.\venv\Scripts\Activate.ps1

# Windows CMD
.\venv\Scripts\activate.bat

# Linux/Mac
source venv/bin/activate
```

4. **Instala dependencias:**
```bash
pip install -r requirements.txt
```

5. **Agrega documentos NICSP:**
   - Coloca archivos `.txt`, `.pdf` o `.docx` en `backend/data/docs/`
   - El sistema procesará automáticamente los documentos al iniciar

### Frontend

1. **Navega a la carpeta frontend:**
```bash
cd frontend
```

2. **Instala dependencias:**
```bash
npm install
```

## Ejecutar el Proyecto

### 1. Inicia el Backend

```bash
cd backend
# Asegúrate de que el entorno virtual esté activado
python app.py
```

**Salida esperada:**
```
Cargando índice FAISS existente...
 * Serving Flask app 'app'
 * Running on http://0.0.0.0:5000
```

> **Nota**: La primera vez generará el índice FAISS, puede tardar unos minutos dependiendo de la cantidad de documentos.

### 2. Inicia el Frontend (en otra terminal)

```bash
cd frontend
npm run dev
```

**Salida esperada:**
```
  ▲ Next.js 16.0.1
  - Local:        http://localhost:3000
  - Ready in 2.5s
```

### 3. Abre el navegador

Visita: **http://localhost:3000**

## Configuración

### Cambiar modelo de Ollama

En `backend/app.py`, línea 34:
```python
llm = Ollama(model="phi3")  # Cambia a "llama3" o "mistral"
```

Modelos disponibles:
- `llama3` - Más preciso, requiere más RAM (~8GB)
- `mistral` - Buen balance calidad/rendimiento
- `phi3` - Más rápido, menos recursos (~4GB RAM)

### Ajustar parámetros de chunking

En `backend/app.py`, línea 24:
```python
CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
```

- `chunk_size`: Tamaño de cada fragmento de texto (tokens)
- `chunk_overlap`: Superposición entre fragmentos para contexto

## Solución de Problemas

### El backend no inicia

**Error:** `ModuleNotFoundError: No module named 'flask_cors'`
```bash
pip install flask-cors
```

**Error:** Ollama no responde
```bash
# Verifica que Ollama esté corriendo
ollama list
# Si no aparece, inicia el servicio
ollama serve
```

### El frontend no conecta

**Error:** `CORS policy blocked`
- Verifica que `flask-cors` esté instalado
- Asegúrate de que el backend esté corriendo en puerto 5000

**Error:** `fetch failed`
- Confirma que el backend esté en `http://localhost:5000`
- Verifica que Ollama esté corriendo con un modelo descargado

### No hay documentos

Si `backend/data/docs/` está vacío:
1. Agrega archivos `.txt` con contenido de las NICSP
2. Reinicia el backend para regenerar el índice
3. Elimina `backend/data/nicsp_index/` para forzar regeneración

## Stack Tecnológico

| Componente | Tecnología | Versión |
|------------|-----------|---------|
| Backend Framework | Flask | 3.1.2 |
| IA/LLM | Ollama | Latest |
| Vector Store | FAISS | 1.12.0 |
| Embeddings | Sentence Transformers | 5.1.2 |
| LangChain | langchain | 1.0.3 |
| Frontend Framework | Next.js | 16.0.1 |
| UI Library | React | 19.2.0 |
| Styling | Tailwind CSS | 4.x |
| Language | Python + TypeScript | 3.x + 5.x |

## Licencia

Este proyecto es de código abierto para fines educativos.
---

**Desarrollado por Sanrio y Jab**
