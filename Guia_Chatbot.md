# Chatbot NICSP — Guía

Este documento explica, qué es este chatbot, cómo funciona la técnica RAG que utiliza, cómo se alimenta con documentos y cómo ponerlo en marcha. Está pensado para cualquier persona, incluyendo quien no tiene experiencia técnica.

---

## ¿Qué es este chatbot?

Es un asistente virtual diseñado para responder preguntas sobre las NICSP (Normas Internacionales de Contabilidad del Sector Público). Puedes escribir preguntas en lenguaje natural (español) y el chatbot busca en una base de documentos y construye una respuesta basada en la información encontrada.

El objetivo es ayudar a usuarios (ciudadanos, funcionarios, estudiantes) a encontrar información normativa rápida y confiable.

---

## ¿Qué significa RAG?

RAG = Retrieval-Augmented Generation. En palabras sencillas:

- Retrieval (recuperación): el sistema primero busca en una colección de documentos (como archivos TXT) las partes que parecen más relevantes para tu pregunta.
- Augmented (aumentado): esas partes encontradas se usan como «evidencia» o contexto adicional.
- Generation (generación): un modelo de lenguaje (IA) usa esa evidencia para generar una respuesta clara y en lenguaje natural.

Por qué es útil: en vez de que la IA invente o se base solo en su memoria, RAG le da fuentes concretas para que la respuesta esté anclada en documentos reales.

---

## Flujo de una pregunta (paso a paso, simple)

1. Tú escribes una pregunta en la web.
2. El backend transforma la pregunta a un embedding (vector) y busca los fragmentos más parecidos en FAISS.
3. Se seleccionan los mejores fragmentos (contexto) y se recortan si son muy largos.
4. Se forma un "prompt" que incluye ese contexto y la pregunta, y se envía al modelo de lenguaje (Ollama).
5. El modelo responde. Antes de devolverlo al usuario, el backend aplica validaciones sencillas (ej.: si la respuesta es muy corta o contiene frases sospechosas, se marca como "No encuentro información").
6. La respuesta aparece en la interfaz web.

---

## ¿Cómo se alimenta con información? (añadir/editar documentos)

- Todos los documentos que alimentan al bot están en `backend/data/docs`.
- Puedes agregar archivos texto: `.txt`, PDF:`.pdf` y Word:`.docx`.
- Para archivos de texto, asegúrate de que estén bien estructurados (títulos, párrafos) y sin duplicados.
- Al iniciar, el servidor crea el índice automáticamente procesando los archivos en `data/docs` listo para hacer preguntas con la informacion que posee.

---

## Mensajes y comportamiento cuando hay problemas

- Si la IA no puede encontrar información suficiente, el bot responde honestamente con mensajes como: "No encuentro esa información específica".
- Si la conexión es lenta, la web muestra un banner de "conexión tardando más de lo normal".
- Si hay timeout, la web muestra un mensaje de "Tiempo de espera agotado".

---

## Buenas prácticas para los documentos fuente

- Evita duplicar textos entre archivos.
- Divide documentos muy largos en secciones con títulos claros.
- Para listas importantes (ej.: las 6 bases de medición), verificar que no se queden al final de un fragmento; si hace falta, aumentar `chunk_size`.
- Mantén convenciones de nombres en los archivos para facilitar búsquedas (ej.: `nicsp_bases_medicion.txt`).

---

## Resumen visual simple

Usuario → (Frontend) → Backend → FAISS (busca fragmentos) → LLM (genera usando contexto) → Backend valida → Usuario obtiene respuesta

---
