# Chatbot NICSP - Asistente de Normas Internacionales

Chatbot inteligente para consultas sobre **Normas Internacionales de Contabilidad del Sector Público (NICSP)** usando **OpenAI API** y RAG (Retrieval-Augmented Generation).

## 🆕 Actualización: Migración a OpenAI API + Optimizaciones v2.0

> **Última actualización (v2.0):** Optimizaciones implementadas - 34% menos costo, mejor calidad.  
> 📖 Ver [OPTIMIZACIONES.md](OPTIMIZACIONES.md) | [ACTUALIZACION.md](ACTUALIZACION.md) | [CAMBIOS.md](CAMBIOS.md)

**Cambios clave v2.0:**
- ✅ OpenAI Embeddings (text-embedding-3-small)
- ✅ MMR para selección de documentos
- ✅ Contexto optimizado a 1000 chars
- ✅ Parámetros ajustados (temp=0.0, top_p=0.2)
- ✅ 34% ahorro en costos

## Descripción

Este proyecto es un MVP de chatbot que combina:
- **Backend**: Python con Flask, LangChain, FAISS y **OpenAI API**
- **Frontend**: Next.js 16 con React y Tailwind CSS
- **IA**: OpenAI GPT-4o-mini (configurable)
- **Base de conocimiento**: Documentos NICSP procesados con embeddings
- **Nueva funcionalidad**: Análisis de archivos PDF con IA

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

### 1. API Key de OpenAI
Necesitas una cuenta de OpenAI y una API key:

**Obtener API Key:**
1. Crea cuenta en: https://platform.openai.com/signup
2. Ve a: https://platform.openai.com/api-keys
3. Crea una nueva API key
4. Cópiala (solo se muestra una vez)

**Costos estimados:**
- Modelo recomendado: `gpt-4o-mini`
- ~$0.000132 USD por consulta
- 1,000 consultas ≈ $0.13 USD

### 2. Python 3.8+
```bash
python --version
```

### 3. Node.js 18+
```bash
node --version
npm --version
```

## 🚀 Instalación Rápida

### Opción 1: Script Automático (Recomendado)

**Windows:**
```cmd
install.bat
```

**Linux/Mac:**
```bash
chmod +x install.sh
./install.sh
```

### Opción 2: Manual

#### Backend

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

5. **Configura tu API key de OpenAI:**
```bash
# Copia el archivo de ejemplo
cp .env.example .env

# Edita .env y añade tu API key
# OPENAI_API_KEY=sk-proj-tu-api-key-aqui
```

6. **Agrega documentos NICSP:**
   - Coloca archivos `.txt`, `.pdf` o `.docx` en `backend/data/docs/`
   - El sistema procesará automáticamente los documentos al iniciar

#### Frontend

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
# Asegúrate de que el entorno virtual esté activado y que .env tenga tu API key
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

### Cambiar modelo de OpenAI

En `backend/.env`:
```env
# Modelos disponibles:
OPENAI_MODEL=gpt-4o-mini      # Recomendado (rápido y económico)
# OPENAI_MODEL=gpt-4o          # Más potente
# OPENAI_MODEL=gpt-4-turbo     # Balance
# OPENAI_MODEL=gpt-3.5-turbo   # Más económico

# Ajustar longitud de respuestas
OPENAI_MAX_TOKENS=220

# Creatividad (0.0-2.0)
OPENAI_TEMPERATURE=0.3
```

### Ajustar parámetros de chunking

En `backend/app.py`:
```python
RecursiveCharacterTextSplitter(
    chunk_size=750,      # Tamaño de fragmentos
    chunk_overlap=120    # Superposición entre fragmentos
)
```

## 🆕 Nuevas Funcionalidades

### 1. Chat Normal
Pregunta sobre las NICSP y el sistema buscará en los documentos locales.

### 2. Análisis de PDF (NUEVO)
1. Haz clic en el botón **📎 PDF**
2. Selecciona un archivo PDF
3. Escribe tu pregunta sobre el PDF
4. El sistema lo analizará con OpenAI

## Solución de Problemas

### Error: "Incorrect API key"
```bash
# Verifica tu API key en backend/.env
OPENAI_API_KEY=sk-proj-XXXXXXXXX
```

### Error: "You exceeded your current quota"
- Añade créditos en: https://platform.openai.com/account/billing
- Verifica tu límite de uso

### Error: `ModuleNotFoundError: No module named 'openai'`
```bash
cd backend
pip install -r requirements.txt
```

### El frontend no conecta

**Error:** `CORS policy blocked`
- Verifica que `flask-cors` esté instalado
- Asegúrate de que el backend esté corriendo en puerto 5000

**Error:** `fetch failed`
- Confirma que el backend esté en `http://localhost:5000`
- Verifica que tu API key de OpenAI esté configurada

### No hay documentos

Si `backend/data/docs/` está vacío:
1. Agrega archivos `.txt` con contenido de las NICSP
2. Reinicia el backend para regenerar el índice
3. Elimina `backend/data/nicsp_index/` para forzar regeneración

## Stack Tecnológico

| Componente | Tecnología | Versión |
|------------|-----------|---------|
| Backend Framework | Flask | 3.1.2 |
| IA/LLM | **OpenAI API** | **gpt-4o-mini** |
| Vector Store | FAISS | 1.12.0 |
| Embeddings | Sentence Transformers | 5.1.2 |
| LangChain | langchain | 1.0.3 |
| Frontend Framework | Next.js | 16.0.1 |
| UI Library | React | 19.2.0 |
| Styling | Tailwind CSS | 4.x |
| Language | Python + TypeScript | 3.x + 5.x |

## 📚 Documentación Adicional

- 📖 [Instrucciones detalladas de OpenAI](INSTRUCCIONES_OPENAI.md) - Guía completa de configuración
- 📋 [Resumen de cambios](CAMBIOS.md) - Detalles de la migración desde Ollama
- 📝 [Guía del Chatbot](Guia_Chatbot.md) - Documentación original

## Licencia

Este proyecto es de código abierto para fines educativos.
---

**Desarrollado por Sanrio y Jab**
