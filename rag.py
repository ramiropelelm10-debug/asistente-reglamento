# =====================================================================
# PARTE 2 de 7: EL CEREBRO, BUSCAR Y RESPONDER            (archivo: rag.py)
# Responsable: [nombre del integrante 2]
#
# Qué hace este archivo:
#   1. Abre la memoria del asistente (ChromaDB) que preparó ingest.py.
#   2. Cuando llega una pregunta, busca los 5 artículos más parecidos.
#   3. Le entrega a Gemini la pregunta, esos artículos y unas reglas (prompt).
#   4. Lee la respuesta y averigua qué artículos usó Gemini.
#   5. Devuelve la respuesta y las tarjetas de los artículos citados.
#   6. Lleva la cuenta de las consultas y los tokens del día (medidor de uso).
#
# La función principal es responder(pregunta). La usa app.py.
# Para probarlo en la terminal:  python rag.py
# =====================================================================
import json
import os
import re
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

# ---------------------------------------------------------------
# 1) Configuración: llave y modelo (se leen del archivo .env)
# ---------------------------------------------------------------
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise SystemExit("Falta GEMINI_API_KEY en el archivo .env")

# Modelo que redacta la respuesta. Si da error, se cambia GEMINI_MODEL en .env
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

# Límites del plan gratuito (se ven en Google AI Studio, en "Límite de frecuencia").
# Si cambian, se pueden cambiar en el archivo .env sin tocar el código.
LIMITE_DIARIO = int(os.getenv("GEMINI_LIMITE_DIA", "500"))    # consultas por día
LIMITE_MINUTO = int(os.getenv("GEMINI_LIMITE_MIN", "15"))     # consultas por minuto
ARCHIVO_USO = Path("uso_gemini.json")                          # aquí se anota el uso del día


class LimiteExcedido(Exception):
    """Se usa cuando se acaba el límite de consultas gratuitas de Gemini."""


# ---------------------------------------------------------------
# 2) Memoria (ChromaDB) y modelo (Gemini)
# ---------------------------------------------------------------
# Convierte la pregunta en números, igual que se hizo con los artículos
embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001",
    google_api_key=API_KEY,
)
# Abre la carpeta chroma_db con los artículos guardados
db = Chroma(persist_directory="chroma_db", embedding_function=embeddings)
# El modelo de lenguaje que redacta la respuesta
llm = ChatGoogleGenerativeAI(model=MODEL, google_api_key=API_KEY)

# ---------------------------------------------------------------
# 3) El prompt: las reglas que se le dan a Gemini
# ---------------------------------------------------------------
PROMPT = """Eres el asistente virtual del reglamento interno de una unidad educativa. \
Respondes dudas de estudiantes, padres de familia y docentes usando SOLO los artículos \
del reglamento que aparecen abajo.

Cómo responder:
1. Empieza citando el artículo, por ejemplo: "Según el artículo 71B, sí es obligatorio ..." \
y explica en pocas palabras el motivo o la condición que establece ese artículo.
2. Si necesitas varios artículos, cítalos todos con su número.
3. No inventes datos, horarios, porcentajes ni sanciones. Usa solo lo que dicen los artículos.
4. Si la respuesta no está en los artículos, responde exactamente: \
"No encontré esa información en el reglamento." y nada más.
5. Responde en el mismo idioma de la pregunta, con un tono claro y respetuoso.
6. Nunca apruebes, niegues ni prometas permisos, justificaciones ni autorizaciones: eso lo decide \
el colegio (regencia o la Dirección). Si la pregunta trata de un permiso, una salida anticipada, \
una justificación de inasistencia, un permiso prolongado o medicamentos, explica el requisito del \
artículo y termina con: "Puedes preparar la carta en la sección Cartas de permiso, imprimirla, \
firmarla y entregarla en regencia. El colegio decide."
7. En una última línea aparte escribe ARTICULOS_USADOS: seguido de los números de artículo \
que usaste, separados por comas (por ejemplo: ARTICULOS_USADOS: 14, 71B). \
Si no usaste ninguno, escribe ARTICULOS_USADOS: NINGUNO.

Artículos del reglamento:
{contexto}

Pregunta: {pregunta}

Respuesta:"""


# ---------------------------------------------------------------
# 4) Funciones de apoyo
# ---------------------------------------------------------------
def _texto(content):
    """Convierte la respuesta del modelo en texto simple."""
    if isinstance(content, str):
        return content
    partes = []
    for bloque in content:
        if isinstance(bloque, str):
            partes.append(bloque)
        elif isinstance(bloque, dict) and bloque.get("type") == "text":
            partes.append(bloque.get("text", ""))
    return "".join(partes)


def _separar(texto):
    """Separa la respuesta de la línea ARTICULOS_USADOS.
    Devuelve (respuesta, lista de artículos usados o None)."""
    m = re.search(r"ARTICULOS_USADOS:(.*)$", texto, flags=re.S | re.I)
    if not m:
        return texto.strip(), None
    usados = [a.upper() for a in re.findall(r"\d+[A-Za-z]?", m.group(1))]
    return texto[: m.start()].strip(), usados


def _es_limite(error):
    """Detecta si el error significa que se acabó el límite de consultas."""
    t = str(error).lower()
    return "429" in t or "resource_exhausted" in t or "quota" in t or "rate limit" in t


# ---------------------------------------------------------------
# 5) El medidor de uso: cuenta las consultas y los tokens del día
#    Es un cálculo aproximado: solo cuenta lo que usa este asistente.
#    El dato oficial está en Google AI Studio (Límite de frecuencia).
# ---------------------------------------------------------------
def _hoy():
    """Día actual según la hora del Pacífico, que es cuando Google reinicia el conteo."""
    try:
        from zoneinfo import ZoneInfo
        return datetime.now(ZoneInfo("America/Los_Angeles")).strftime("%Y-%m-%d")
    except Exception:
        return (datetime.now(timezone.utc) - timedelta(hours=8)).strftime("%Y-%m-%d")


def _hora_reinicio():
    """Hora de Bolivia a la que se renuevan las consultas del día."""
    try:
        from zoneinfo import ZoneInfo
        pacifico, bolivia = ZoneInfo("America/Los_Angeles"), ZoneInfo("America/La_Paz")
        manana = (datetime.now(pacifico) + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        return manana.astimezone(bolivia).strftime("%H:%M")
    except Exception:
        return "03:00"


def _leer_uso():
    """Lee el archivo de uso. Si es de otro día, empieza de cero."""
    try:
        datos = json.loads(ARCHIVO_USO.read_text(encoding="utf-8"))
    except Exception:
        datos = {}
    if datos.get("dia") != _hoy():
        datos = {"dia": _hoy(), "consultas": 0, "tokens": 0, "marcas": []}
    return datos


def _tokens(mensaje):
    """Tokens que gastó una respuesta (Gemini los informa en usage_metadata)."""
    meta = getattr(mensaje, "usage_metadata", None) or {}
    try:
        return int(meta.get("total_tokens", 0))
    except Exception:
        return 0


def registrar_uso(tokens=0):
    """Anota una consulta más. 'marcas' guarda la hora de las consultas del último minuto."""
    datos = _leer_uso()
    ahora = time.time()
    datos["consultas"] += 1
    datos["tokens"] += int(tokens or 0)
    datos["marcas"] = [m for m in datos.get("marcas", []) if ahora - m < 60] + [ahora]
    try:
        ARCHIVO_USO.write_text(json.dumps(datos), encoding="utf-8")
    except Exception:
        pass  # si no se puede guardar, el asistente sigue funcionando


def uso_actual():
    """Devuelve el uso del día para mostrarlo en el medidor."""
    datos = _leer_uso()
    ahora = time.time()
    return {
        "consultas": datos["consultas"],
        "tokens": datos["tokens"],
        "limite": LIMITE_DIARIO,
        "restantes": max(LIMITE_DIARIO - datos["consultas"], 0),
        "ultimo_minuto": len([m for m in datos.get("marcas", []) if ahora - m < 60]),
        "limite_minuto": LIMITE_MINUTO,
        "reinicio": _hora_reinicio(),
    }


# ---------------------------------------------------------------
# 6) La función principal: responder una pregunta
# ---------------------------------------------------------------
def responder(pregunta, k=5):
    """Devuelve (respuesta, fuentes). Cada fuente es un diccionario
    con el número de artículo, el capítulo y el texto original."""
    try:
        # a) Buscar los k artículos más parecidos a la pregunta
        docs = db.similarity_search(pregunta, k=k)
        contexto = "\n\n".join(d.page_content for d in docs)
        # b) Pedirle la respuesta a Gemini, con las reglas y los artículos
        bruto = llm.invoke(PROMPT.format(contexto=contexto, pregunta=pregunta))
    except Exception as e:
        if _es_limite(e):
            raise LimiteExcedido(str(e))
        raise

    # Se anota la consulta en el medidor de uso
    registrar_uso(_tokens(bruto))

    # c) Separar la respuesta de la línea con los artículos usados
    respuesta, usados = _separar(_texto(bruto.content))

    if usados is None:  # Gemini no puso la línea: se muestran todos, salvo "no encontré"
        usados = [] if "No encontré esa información" in respuesta else None

    # d) Armar las tarjetas solo con los artículos que Gemini usó
    fuentes, vistos = [], set()
    for d in docs:
        art = d.metadata.get("articulo", "s/n")
        if art in vistos:
            continue
        if usados is not None and art not in usados:
            continue
        vistos.add(art)
        fuentes.append(
            {
                "articulo": art,
                "capitulo": d.metadata.get("capitulo", ""),
                "texto": d.page_content.split("\n", 1)[-1],
            }
        )
    return respuesta, fuentes


# ---------------------------------------------------------------
# 7) Prueba en la terminal:  python rag.py
# ---------------------------------------------------------------
if __name__ == "__main__":
    print("Asistente listo. Escribe tu pregunta (o 'salir').")
    while True:
        pregunta = input("\nTú: ").strip()
        if pregunta.lower() in ("salir", "exit", ""):
            break
        try:
            texto, fuentes = responder(pregunta)
        except LimiteExcedido:
            print("\nBot: Hay muchas consultas en este momento. Intenta de nuevo en un minuto.")
            continue
        print(f"\nBot: {texto}")
        if fuentes:
            print("Artículos citados:", ", ".join(f["articulo"] for f in fuentes))