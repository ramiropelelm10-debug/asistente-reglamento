# Asistente del Reglamento

Asistente virtual que responde dudas sobre el reglamento interno de una unidad educativa,
citando el artículo que respalda cada respuesta. También prepara cartas de permiso en PDF
(salida anticipada, justificación de inasistencia, permiso prolongado y medicamentos).

Hecho con **Streamlit**, **LangChain**, **ChromaDB** y **Gemini**.

> El reglamento incluido es un documento ficticio, preparado solo para las pruebas de un proyecto escolar.

## Cómo funciona

| Archivo | Qué hace |
|---|---|
| `ingest.py` | Lee el PDF de `data/`, lo corta por artículos y guarda los embeddings en `chroma_db/` |
| `rag.py` | Busca los artículos más parecidos a la pregunta y le pide la respuesta a Gemini |
| `app.py` | La página principal y el menú |
| `paginas.py` | Las pantallas y el chat |
| `cartas.py`, `carta_pdf.py`, `validar.py` | El formulario de cartas, su revisión y el PDF |
| `estilos.py` | El diseño |

## Usarlo en tu computadora

```bash
python -m venv .venv
.venv\Scripts\activate        # en Windows
pip install -r requirements.txt
```

Crea un archivo `.env` con tu llave de Gemini (de Google AI Studio):

```
GEMINI_API_KEY=tu_llave
```

Y abre la app:

```bash
streamlit run app.py
```

Si cambias el PDF del reglamento, vuelve a crear la base con `python ingest.py`.

## Publicarlo en Streamlit Community Cloud

1. Entra a [share.streamlit.io](https://share.streamlit.io) con tu cuenta de GitHub.
2. Elige este repositorio, la rama `main` y el archivo `app.py`.
3. En **Advanced settings**, elige Python 3.13 y en **Secrets** escribe:
   ```toml
   GEMINI_API_KEY = "tu_llave"
   ```
4. Presiona **Deploy**.

**Importante:** la llave nunca se sube a GitHub. El archivo `.env` está en `.gitignore`.
