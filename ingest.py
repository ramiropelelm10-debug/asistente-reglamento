# =====================================================================
# PARTE 1 de 7: PREPARAR EL REGLAMENTO                (archivo: ingest.py)
# Responsable: [nombre del integrante 1]
#
# Qué hace este archivo (se ejecuta una vez, y otra vez si cambia el PDF):
#   1. Lee el texto del PDF del reglamento (carpeta data/).
#   2. Lo corta en trozos, uno por cada artículo.
#   3. Convierte cada trozo en números (embeddings) con el modelo de Gemini.
#   4. Guarda los trozos y sus números en ChromaDB (carpeta chroma_db/).
#
# Cómo se ejecuta (con el entorno activado):  python ingest.py
# =====================================================================
import os
import re
import shutil
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from pypdf import PdfReader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

# ---------------------------------------------------------------
# 1) Ajustes
# ---------------------------------------------------------------
DATA_DIR = "data"      # carpeta donde se guarda el PDF del reglamento
DB_DIR = "chroma_db"   # carpeta donde se guarda la memoria del asistente

# Reglas (expresiones regulares) para reconocer dónde empieza un artículo
# y dónde empieza un capítulo. Reconocen, por ejemplo:
# "Artículo 12 (...)", "Artículo 71B." o "Art. 5.-"
RE_ARTICULO = re.compile(r"^[ \t]*Art(?:[íi]culo|\.)\s*(\d+[A-Za-z]?)\s*[°º]?\s*[(.\-–:]", re.M)
RE_CAPITULO = re.compile(r"^[ \t]*CAP[ÍI]TULO\s+[IVXLCDM]+.*$", re.M)

# Cortador por tamaño: solo se usa si un artículo es muy largo
# o si el PDF no tiene artículos reconocibles.
splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=150)


# ---------------------------------------------------------------
# 2) Leer el PDF
# ---------------------------------------------------------------
def limpiar(texto):
    """Cambia los saltos de línea y los espacios repetidos por un solo espacio."""
    return re.sub(r"\s+", " ", texto).strip()


def leer_pdf(ruta):
    """Devuelve todo el texto del PDF, página por página."""
    lector = PdfReader(ruta)
    return "\n".join((pagina.extract_text() or "") for pagina in lector.pages)


# ---------------------------------------------------------------
# 3) Cortar el texto: un trozo por artículo
# ---------------------------------------------------------------
def cortar_por_articulos(texto, archivo):
    """Un fragmento por artículo, guardando su número y su capítulo."""
    articulos = list(RE_ARTICULO.finditer(texto))   # dónde empieza cada artículo
    capitulos = list(RE_CAPITULO.finditer(texto))   # dónde empieza cada capítulo
    docs = []

    for i, m in enumerate(articulos):
        # El artículo empieza donde lo encontró la regla
        # y termina donde empieza el siguiente (o al final del texto).
        inicio = m.start()
        fin = articulos[i + 1].start() if i + 1 < len(articulos) else len(texto)

        # Si entre dos artículos empieza un capítulo nuevo, el artículo termina ahí
        for c in capitulos:
            if inicio < c.start() < fin:
                fin = c.start()
                break

        # Capítulo al que pertenece este artículo (el último que empezó antes)
        capitulo = ""
        for c in capitulos:
            if c.start() < inicio:
                capitulo = limpiar(c.group(0))

        cuerpo = limpiar(texto[inicio:fin])
        contenido = f"{capitulo}\n{cuerpo}" if capitulo else cuerpo

        # Datos que se guardan junto al trozo: sirven para citar el artículo después
        metadatos = {
            "archivo": archivo,
            "articulo": m.group(1).upper(),
            "capitulo": capitulo,
        }

        # Si un artículo es muy largo, se parte en trozos del mismo artículo
        if len(contenido) > 1500:
            for trozo in splitter.split_text(contenido):
                docs.append(Document(page_content=trozo, metadata=dict(metadatos)))
        else:
            docs.append(Document(page_content=contenido, metadata=metadatos))
    return docs


# ---------------------------------------------------------------
# 4) Cargar todos los PDFs de la carpeta data/
# ---------------------------------------------------------------
def cargar_documentos():
    docs = []
    for ruta in sorted(Path(DATA_DIR).glob("*.pdf")):
        texto = leer_pdf(ruta)
        por_articulo = cortar_por_articulos(texto, ruta.name)
        if len(por_articulo) >= 3:
            print(f"{ruta.name}: {len(por_articulo)} fragmentos (uno por artículo)")
            docs.extend(por_articulo)
        else:
            # Plan B: si el PDF no tiene artículos reconocibles, se corta por tamaño
            base = Document(page_content=limpiar(texto), metadata={"archivo": ruta.name})
            trozos = splitter.split_documents([base])
            for t in trozos:
                t.metadata.update({"articulo": "s/n", "capitulo": ""})
            print(f"{ruta.name}: sin artículos reconocibles, {len(trozos)} fragmentos por tamaño")
            docs.extend(trozos)
    return docs


# ---------------------------------------------------------------
# 5) Programa principal: convertir en números y guardar en ChromaDB
# ---------------------------------------------------------------
def main():
    # La llave de Gemini se lee del archivo .env (nunca se escribe en el código)
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise SystemExit("Falta GEMINI_API_KEY en el archivo .env")

    chunks = cargar_documentos()
    if not chunks:
        raise SystemExit("No encontré PDFs con texto en la carpeta data/")

    # Si ningún fragmento tiene número de artículo, el PDF probablemente se leyó mal
    # (por ejemplo, un PDF dañado que convierte "Artículo" en símbolos raros).
    # Se detiene ANTES de borrar la base buena, salvo que se pida a propósito:
    #   python ingest.py --por-tamano
    if all(c.metadata.get("articulo") == "s/n" for c in chunks) and "--por-tamano" not in sys.argv:
        raise SystemExit(
            "No reconocí ningún artículo en los PDFs de data/. La base chroma_db/ NO se modificó.\n"
            "Revisa que el PDF no esté dañado. Si de verdad quieres cortarlo por tamaño, "
            "ejecuta: python ingest.py --por-tamano"
        )
    print(f"Total de fragmentos: {len(chunks)}")

    # Se borra la base anterior para no duplicar artículos
    if os.path.exists(DB_DIR):
        shutil.rmtree(DB_DIR)

    # Modelo de Gemini que convierte textos en números (embeddings)
    embeddings = GoogleGenerativeAIEmbeddings(
        model="gemini-embedding-001",
        google_api_key=api_key,
    )
    # Base de datos ChromaDB: guarda los trozos y sus números en chroma_db/
    db = Chroma(persist_directory=DB_DIR, embedding_function=embeddings)

    # Se guarda de 50 en 50, con una pausa, para no pasar el límite gratuito
    for i in range(0, len(chunks), 50):
        db.add_documents(chunks[i : i + 50])
        print(f"Guardados {min(i + 50, len(chunks))}/{len(chunks)}")
        time.sleep(2)

    print("Listo. Base de datos creada en chroma_db/")


if __name__ == "__main__":
    main()