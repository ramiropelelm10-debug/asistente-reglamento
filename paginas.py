# =====================================================================
# PARTE 4 de 7: LAS PANTALLAS Y EL CHAT                (archivo: paginas.py)
# Responsable: [nombre del integrante 4]
#
# Qué hace este archivo:
#   Contiene lo que se dibuja en cada pantalla:
#   1. mostrar_encabezado()  -> la portada de la pantalla de Inicio.
#   2. pagina_reglamento()   -> los temas que se pueden consultar y cómo funciona.
#   3. pagina_historial()    -> las preguntas que se hicieron en la sesión.
#   4. conversacion()        -> el chat: mensaje de bienvenida y burbujas.
#   5. mostrar_fuentes()     -> las tarjetas desplegables de los artículos citados.
#
# Estas funciones las llama app.py según la pantalla en que está la persona.
# =====================================================================
from html import escape

import streamlit as st

from estilos import AVATAR_BOT, NOMBRE_APP


# ---------------------------------------------------------------
# 1) Portada de la pantalla de Inicio
# ---------------------------------------------------------------
def mostrar_encabezado():
    st.markdown(
        '<div class="tagline"><i class="ico ico-sun"></i><span class="ln"></span>'
        '<em>Tu norma, siempre a un clic</em><span class="ln"></span></div>'
        '<div class="hero"><div class="hero-art"></div><div class="hero-logo"></div>'
        '<div class="hero-texto">'
        f'<div class="hero-kicker">{NOMBRE_APP.upper()}</div>'
        '<h1 class="hero-title">Asistente del<br><span class="azul">Reglamento</span></h1>'
        '<p class="hero-sub">Resuelve tus dudas sobre el reglamento interno al instante, '
        "con el artículo que respalda cada respuesta.</p>"
        '<span class="chip"><i class="ico ico-doc"></i>Cita el artículo</span>'
        '<span class="chip"><i class="ico ico-shield"></i>Solo el reglamento</span>'
        '<span class="chip"><i class="ico ico-chat"></i>Responde en tu idioma</span>'
        "</div></div>",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------
# 2) Tarjetas desplegables con el texto original de cada artículo
# ---------------------------------------------------------------
def mostrar_fuentes(fuentes):
    """Una fila de etiquetas ("Art. 20", "Art. 21"...). Al tocar una, se abre el texto del artículo."""
    if not fuentes:
        return
    with st.container(horizontal=True, gap="small"):
        for f in fuentes:
            etiqueta = "Fragmento" if f["articulo"] == "s/n" else f"Art. {f['articulo']}"
            with st.popover(etiqueta, icon=":material/description:"):
                if f["capitulo"]:
                    st.caption(f["capitulo"])   # nombre del capítulo, en letra pequeña
                st.write(f["texto"])            # texto original del artículo


# ---------------------------------------------------------------
# 3) Pantalla "Reglamento"
# ---------------------------------------------------------------
def pagina_reglamento():
    st.markdown('<div class="pagina-titulo">Reglamento</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="card"><h3>Temas que puedes consultar</h3><ul>'
        "<li>Asistencia y puntualidad</li><li>Uniforme</li><li>Uso del celular</li>"
        "<li>Evaluación y promoción</li><li>Faltas y sanciones</li></ul></div>"
        '<div class="card"><h3>Cómo funciona</h3>'
        '<div class="paso"><span class="num">1</span><span>Escribes tu duda.</span></div>'
        '<div class="paso"><span class="num">2</span><span>El asistente busca los artículos relacionados.</span></div>'
        '<div class="paso"><span class="num">3</span><span>Responde citando el artículo que lo respalda.</span></div>'
        "<p>Las respuestas se basan únicamente en el reglamento interno. "
        "Ante cualquier duda, consulta con la Dirección.</p></div>",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------
# 4) Pantalla "Historial": preguntas de esta sesión
# ---------------------------------------------------------------
def pagina_historial():
    st.markdown('<div class="pagina-titulo">Historial</div>', unsafe_allow_html=True)
    preguntas = [m["content"] for m in st.session_state.mensajes if m["role"] == "user"]
    if not preguntas:
        st.markdown(
            '<div class="vacio">Todavía no hiciste ninguna pregunta en esta sesión.</div>',
            unsafe_allow_html=True,
        )
        return
    # escape() evita que símbolos como < o > rompan la página
    items = "".join(f"<li>{escape(p)}</li>" for p in reversed(preguntas))
    st.markdown(
        f'<div class="card"><h3>Tus preguntas de esta sesión</h3><ul>{items}</ul></div>',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------
# 5) El chat: bienvenida y conversación guardada
# ---------------------------------------------------------------
SUGERENCIAS = [
    "¿Es obligatorio usar el uniforme?",
    "¿Puedo usar el celular en clase?",
    "¿Cómo justifico una inasistencia?",
    "¿Qué pasa si llego tarde?",
]


def _preguntar(texto):
    """Guarda la pregunta elegida; app.py la responde como si se hubiera escrito."""
    st.session_state.pendiente = texto


def conversacion():
    # Si todavía no hay mensajes, se muestra el saludo del asistente
    if not st.session_state.mensajes:
        with st.chat_message("assistant", avatar=AVATAR_BOT):
            st.markdown(
                "Hola, soy el asistente virtual del reglamento interno. Puedes preguntarme sobre "
                "**asistencia y puntualidad**, **uniforme**, **uso del celular**, "
                "**evaluación y promoción** o **faltas y sanciones**."
            )
        # Preguntas de ejemplo: con un clic se envían al asistente (app.py las lee de "pendiente")
        st.markdown('<div class="sug-titulo"><i class="ico ico-spark"></i>Prueba con una de estas preguntas</div>',
                    unsafe_allow_html=True)
        with st.container(key="sugerencias"):
            columnas = st.columns(2)
            for i, texto in enumerate(SUGERENCIAS):
                columnas[i % 2].button(texto, key=f"sug_{i}", on_click=_preguntar, args=(texto,),
                                       use_container_width=True)

    # Se dibujan todos los mensajes guardados (preguntas y respuestas)
    for m in st.session_state.mensajes:
        avatar = AVATAR_BOT if m["role"] == "assistant" else None
        with st.chat_message(m["role"], avatar=avatar):
            st.markdown(m["content"])
            mostrar_fuentes(m.get("fuentes", []))