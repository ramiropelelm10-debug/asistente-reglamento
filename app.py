# =====================================================================
# PARTE 3 de 7: LA PÁGINA PRINCIPAL Y EL MENÚ              (archivo: app.py)
# Responsable: [nombre del integrante 3]
#
# Qué hace este archivo (es el "director de orquesta"):
#   1. Configura la página y aplica el diseño (estilos.py).
#   2. Crea la memoria de la sesión: los mensajes y la pantalla actual.
#   3. Arma la barra lateral con el menú: Inicio, Tu duda, Reglamento,
#      Cartas de permiso, Historial y el botón Nueva conversación.
#   4. Decide qué pantalla mostrar (paginas.py y cartas.py).
#   5. Cuando alguien escribe una pregunta, llama a responder() (rag.py)
#      y muestra la respuesta con las tarjetas de los artículos.
#      (La caja de pregunta se oculta en la pantalla de Cartas de permiso.)
#   6. Muestra el medidor de consultas de Gemini y avisa cuando quedan pocas.
#   7. Pide al navegador que no traduzca la página.
#
# Cómo se abre la página:  streamlit run app.py
# =====================================================================
import time

import streamlit as st

from cartas import pantalla_cartas
from estilos import AVATAR_BOT, HAY_LOGO, LOGO, NOMBRE_APP, PANTALLA_CARGA, aplicar_estilos
from paginas import (conversacion, mostrar_encabezado, mostrar_fuentes,
                     pagina_historial, pagina_reglamento)
# Ojo: rag.py se importa más abajo, DESPUÉS de mostrar la pantalla de carga,
# porque abrir ChromaDB y conectar con Gemini tarda unos segundos.

TIEMPO_MINIMO_CARGA = 1.5   # segundos que se ve la pantalla de carga al entrar (0 = solo lo necesario)

# ---------------------------------------------------------------
# 1) Configuración de la página y diseño
#    (set_page_config tiene que ser lo primero que se ejecuta de Streamlit)
# ---------------------------------------------------------------
st.set_page_config(
    page_title="Asistente del Reglamento",
    page_icon=LOGO if HAY_LOGO else ":material/school:",
    layout="centered",
    initial_sidebar_state="expanded",   # la barra lateral empieza abierta
)
aplicar_estilos()

# ---------------------------------------------------------------
# 1b) Pantalla de carga: se muestra al entrar mientras se prepara el asistente
#     (la primera vez se abre ChromaDB y se conecta con Gemini; las siguientes es rápido)
# ---------------------------------------------------------------
primera_vez = "cargado" not in st.session_state
if primera_vez:
    carga = st.empty()
    carga.markdown(PANTALLA_CARGA, unsafe_allow_html=True)
    inicio = time.time()

from rag import LimiteExcedido, responder, uso_actual  # noqa: E402  (va aquí a propósito)

if primera_vez:
    time.sleep(max(0.0, TIEMPO_MINIMO_CARGA - (time.time() - inicio)))
    carga.empty()
    st.session_state.cargado = True

# ---------------------------------------------------------------
# 2) Memoria de la sesión
#    "mensajes" guarda la conversación; "vista" guarda la pantalla actual.
# ---------------------------------------------------------------
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []
if "vista" not in st.session_state:
    st.session_state.vista = "inicio"

# La caja de pregunta se crea primero para saber si la persona escribió algo.
# No se muestra en la pantalla de Cartas de permiso, porque ahí no hace falta.
pregunta = None
if st.session_state.vista != "cartas":
    pregunta = st.chat_input("Escribe tu pregunta sobre el reglamento...")
# Si se tocó una pregunta sugerida (paginas.py), se usa como si se hubiera escrito
pendiente = st.session_state.pop("pendiente", None)
if not pregunta and pendiente:
    pregunta = pendiente
if pregunta:
    st.session_state.mensajes.append({"role": "user", "content": pregunta})
    st.session_state.vista = "duda"


def ir(vista):
    """Cambia la pantalla que se muestra."""
    st.session_state.vista = vista


def nueva_conversacion():
    """Borra la conversación y vuelve al inicio."""
    st.session_state.mensajes = []
    st.session_state.vista = "inicio"


# ---------------------------------------------------------------
# 3) Barra lateral con el menú
# ---------------------------------------------------------------
NAV = [  # (nombre interno, texto del botón, ícono)
    ("inicio", "Inicio", ":material/chat_bubble:"),
    ("duda", "Tu duda", ":material/menu_book:"),
    ("reglamento", "Reglamento", ":material/description:"),
    ("cartas", "Cartas de permiso", ":material/mail:"),
    ("historial", "Historial", ":material/forum:"),
]

with st.sidebar:
    # Logo y nombre arriba del menú
    st.markdown(
        '<div class="brand"><div class="brand-logo"></div><div class="brand-text">'
        '<span class="b1">ASISTENTE DEL</span><span class="b2">REGLAMENTO</span>'
        '<span class="b3">EDUCACIÓN</span></div></div>',
        unsafe_allow_html=True,
    )
    # Un botón por cada pantalla; el de la pantalla actual se ve resaltado
    for clave, texto, icono in NAV:
        st.button(
            texto,
            key=f"nav_{clave}",
            icon=icono,
            type="primary" if st.session_state.vista == clave else "secondary",
            on_click=ir,
            args=(clave,),
        )
    st.divider()
    st.button("Nueva conversación", key="nueva", icon=":material/add:", on_click=nueva_conversacion)
    medidor = st.empty()   # aquí se dibuja el medidor de consultas de Gemini
    # Pie del menú
    st.markdown(
        '<div class="side-foot"><i class="ico ico-cap"></i><div>'
        f'<div class="t">{NOMBRE_APP}</div>'
        '<div class="s">Formación con valores,<br>para un mejor futuro.</div>'
        "</div></div>",
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------
# 3b) Medidor de consultas de Gemini (el cálculo está en rag.py)
# ---------------------------------------------------------------
UMBRALES = (100, 50, 20, 10, 0)   # cuando quedan tantas consultas, aparece un aviso


def pintar_medidor():
    """Dibuja la barra de consultas usadas hoy y los avisos de la barra lateral."""
    uso = uso_actual()
    usado, limite = uso["consultas"], uso["limite"]
    porcentaje = min(100, round(100 * usado / limite)) if limite else 0
    color = "#4DA3FF" if porcentaje < 70 else ("#F7A04A" if porcentaje < 90 else "#FF6B6B")
    tokens = f"{uso['tokens']:,}".replace(",", ".")
    html = (
        '<div class="medidor">'
        f'<div class="medidor-fila"><span>Consultas de Gemini hoy</span><b>{usado} / {limite}</b></div>'
        f'<div class="medidor-barra"><div class="medidor-relleno" style="width:{porcentaje}%;background:{color}"></div></div>'
        f'<div class="medidor-pie">Tokens usados hoy: {tokens}</div></div>'
    )
    if uso["restantes"] == 0:
        html += (f'<div class="aviso aviso-error">Se acabaron las consultas de hoy. '
                 f'Se renuevan a las {uso["reinicio"]} (hora de Bolivia).</div>')
    elif uso["restantes"] <= UMBRALES[0]:
        html += f'<div class="aviso aviso-alerta">Quedan pocas consultas hoy: {uso["restantes"]}.</div>'
    if uso["ultimo_minuto"] >= uso["limite_minuto"] - 2:
        html += '<div class="aviso aviso-alerta">Muchas consultas en el último minuto. Espera unos segundos.</div>'
    medidor.markdown(html, unsafe_allow_html=True)


def avisar_si_quedan_pocas():
    """Muestra un aviso emergente al cruzar cada umbral (100, 50, 20, 10 y 0 consultas)."""
    restantes = uso_actual()["restantes"]
    umbral = min((u for u in UMBRALES if restantes <= u), default=None)
    if umbral is not None and st.session_state.get("umbral_avisado", 10**9) > umbral:
        st.session_state.umbral_avisado = umbral
        st.toast(f"Quedan {restantes} consultas de Gemini hoy.", icon=":material/warning:")


pintar_medidor()

# ---------------------------------------------------------------
# 4) Decidir qué pantalla mostrar
# ---------------------------------------------------------------
vista = st.session_state.vista

if vista == "inicio":
    mostrar_encabezado()
if vista in ("inicio", "duda"):
    if vista == "duda":
        st.markdown('<div class="pagina-titulo">Tu duda</div>', unsafe_allow_html=True)
    conversacion()
elif vista == "reglamento":
    pagina_reglamento()
elif vista == "cartas":
    st.markdown('<div class="pagina-titulo">Cartas de permiso</div>', unsafe_allow_html=True)
    pantalla_cartas()
elif vista == "historial":
    pagina_historial()

# ---------------------------------------------------------------
# 5) Responder la pregunta (rag.py) y guardar la respuesta
# ---------------------------------------------------------------
if pregunta:
    with st.chat_message("assistant", avatar=AVATAR_BOT):
        with st.spinner("Consultando el reglamento..."):
            try:
                texto, fuentes = responder(pregunta)
            except LimiteExcedido:
                texto = "Hay muchas consultas en este momento. Espera un minuto e intenta de nuevo."
                fuentes = []
            except Exception:
                texto = "Hubo un problema al consultar el asistente. Intenta de nuevo en unos segundos."
                fuentes = []
        st.markdown(texto)
        mostrar_fuentes(fuentes)

    st.session_state.mensajes.append(
        {"role": "assistant", "content": texto, "fuentes": fuentes}
    )
    # Se actualiza el medidor y se avisa si quedan pocas consultas
    pintar_medidor()
    avisar_si_quedan_pocas()

# ---------------------------------------------------------------
# 7) Pide al navegador que no traduzca la página (evita un error de Chrome)
# ---------------------------------------------------------------
try:
    import streamlit.components.v1 as components

    components.html(
        """
        <script>
        const d = window.parent.document;
        d.documentElement.setAttribute('lang', 'es');
        d.documentElement.setAttribute('translate', 'no');
        if (!d.querySelector('meta[name="google"]')) {
            const m = d.createElement('meta');
            m.name = 'google';
            m.content = 'notranslate';
            d.head.appendChild(m);
        }
        </script>
        """,
        height=0,
    )
except Exception:
    pass