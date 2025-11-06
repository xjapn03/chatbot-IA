# Backend - Chatbot NICSP

API Flask con LangChain, FAISS y Ollama para el chatbot NICSP.

## Inicio Rápido

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual (Windows)
.\venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt

# Iniciar servidor
python app.py
```

El servidor estará disponible en: `http://localhost:5000`

## Estructura

```
backend/
├── app.py                  # Servidor principal Flask
├── requirements.txt        # Dependencias Python
└── data/
    ├── docs/              # Documentos fuente (txt, pdf)
    └── nicsp_index/       # Índice FAISS (auto-generado)
```

## 🔌 API Endpoints

### POST `/chat`

Envía un mensaje y recibe una respuesta del chatbot.

**Request:**
```json
{
  "message": "¿Qué es la NICSP 1?"
}
```

**Response:**
```json
{
  "response": "La NICSP 1 establece la manera general de presentar los estados financieros..."
}
```

**Error:**
```json
{
  "error": "No message provided"
}
```

## Configuración

### Cambiar modelo de Ollama

En `app.py`, línea 34:
```python
llm = Ollama(model="phi3")
```

Opciones disponibles:
- `phi3` - Ligero (~2.3GB RAM)
- `llama3` - Preciso (~8GB RAM)
- `mistral` - Equilibrado (~6GB RAM)

### Ajustar tamaño de chunks

En `app.py`, línea 24:
```python
CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
```

- **chunk_size**: Tamaño del fragmento (recomendado: 500-2000)
- **chunk_overlap**: Superposición entre chunks (recomendado: 10-20% de chunk_size)

### Cambiar embeddings

En `app.py`, línea 16:
```python
embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
```

Alternativas:
- `all-MiniLM-L6-v2` - Rápido, ligero (actual)
- `paraphrase-multilingual-MiniLM-L12-v2` - Multilenguaje
- `all-mpnet-base-v2` - Más preciso pero más pesado

## Agregar Documentos

1. Coloca archivos `.txt` en `data/docs/`
2. Elimina la carpeta `data/nicsp_index/` si existe
3. Reinicia el servidor - el índice se regenerará automáticamente

## Troubleshooting

### Error: "No module named 'flask_cors'"
```bash
pip install flask-cors
```

### Error: Ollama connection refused
```bash
# Verifica que Ollama esté corriendo
ollama serve

# Verifica modelos descargados
ollama list
```

### El índice FAISS no se genera
- Asegúrate de que haya archivos en `data/docs/`
- Verifica permisos de escritura en `data/nicsp_index/`
- Revisa logs en la consola para errores específicos

### Respuestas lentas
- Usa un modelo más ligero (phi3)
- Reduce el chunk_size
- Considera limitar el número de documentos recuperados

## Dependencias Principales

| Paquete | Versión | Propósito |
|---------|---------|-----------|
| Flask | 3.1.2 | Framework web |
| Flask-CORS | 5.0.0 | Permitir peticiones CORS |
| langchain | 1.0.3 | Framework de IA |
| faiss-cpu | 1.12.0 | Búsqueda vectorial |
| sentence-transformers | 5.1.2 | Embeddings |
| langchain-core | 1.0.3 | Core de LangChain |

## Seguridad

**Nota**: Este es un MVP para desarrollo. Para producción:

- [ ] Agregar autenticación (JWT, OAuth)
- [ ] Implementar rate limiting
- [ ] Validar y sanitizar inputs
- [ ] Usar variables de entorno para configuración
- [ ] Agregar logging robusto
- [ ] Implementar manejo de errores completo