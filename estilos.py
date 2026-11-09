# =====================================================================
# PARTE 5 de 7: EL DISEÑO AZUL Y NARANJA               (archivo: estilos.py)
# Responsable: [nombre del integrante 5]
#
# Qué hace este archivo:
#   1. Guarda los datos de la marca: nombre, logo y avatar del asistente.
#   2. Dibuja los íconos y las olas de colores (imágenes SVG hechas con código).
#   3. Contiene los estilos CSS: colores, letra Poppins, barra lateral,
#      burbujas del chat, tarjetas de artículos, cuadro de pregunta y
#      formularios (campos, etiquetas y botones de las cartas)
#      y cuadros de aviso con colores legibles.
#   5. Mejora el medidor de consultas, oculta los textos en inglés de Streamlit
#      y deja siempre visible la forma de abrir la barra lateral.
#   4. La función aplicar_estilos() inyecta todo eso en la página.
#
# La función principal es aplicar_estilos(). La llama app.py.
# Paleta: azul marino #0B2A5B, azul #1E6BFF, naranja #F28C28, fondo #F5F9FF
# =====================================================================
import base64
import io
import os
from urllib.parse import quote

import streamlit as st
from PIL import Image

# ---------------------------------------------------------------
# 1) Datos de la marca (los usan también app.py y paginas.py)
# ---------------------------------------------------------------
NOMBRE_APP = "Asistente virtual para educación"
LOGO = "assets/logo.png"            # el logo está en la carpeta assets/
HAY_LOGO = os.path.exists(LOGO)     # si no existe el archivo, la página funciona igual
AVATAR_BOT = LOGO if HAY_LOGO else None   # imagen que aparece junto a las respuestas


# ---------------------------------------------------------------
# 2) Recursos gráficos: se generan aquí, no hace falta instalar nada
# ---------------------------------------------------------------
def svg_uri(svg):
    """Convierte un dibujo SVG en una dirección que CSS puede usar como imagen."""
    return "data:image/svg+xml," + quote(svg)


def logo_uri(ruta, lado=256):
    """Convierte el logo en una dirección de imagen (base64) para usarlo en CSS."""
    img = Image.open(ruta).convert("RGBA").resize((lado, lado))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


NS = "xmlns='http://www.w3.org/2000/svg'"
# Cada ícono es un dibujo SVG. El nombre entre guiones bajos se reemplaza en el CSS.
ICONOS = {
    "__ICO_DOC__": f"<svg {NS} viewBox='0 0 24 24'><path d='M6 2h8l6 6v14H6z' fill='#2F8CFF'/><path d='M14 2v6h6z' fill='#BBD6FA'/><rect x='9' y='12' width='8' height='1.8' fill='#FFFFFF'/><rect x='9' y='16' width='8' height='1.8' fill='#FFFFFF'/></svg>",
    "__ICO_SHIELD__": f"<svg {NS} viewBox='0 0 24 24'><path d='M12 2l8 3v6c0 5-3.5 9-8 11-4.5-2-8-6-8-11V5z' fill='#2F8CFF'/><path d='M8.5 12l2.5 2.5 4.5-5' stroke='#FFFFFF' stroke-width='2' fill='none' stroke-linecap='round' stroke-linejoin='round'/></svg>",
    "__ICO_CHAT__": f"<svg {NS} viewBox='0 0 24 24'><path d='M3 4h18v12H9l-6 5z' fill='#2F8CFF'/><circle cx='8' cy='10' r='1.3' fill='#FFFFFF'/><circle cx='12' cy='10' r='1.3' fill='#FFFFFF'/><circle cx='16' cy='10' r='1.3' fill='#FFFFFF'/></svg>",
    "__ICO_SUN__": f"<svg {NS} viewBox='0 0 24 24'><path d='M7 16a5 5 0 0 1 10 0z' fill='#F7A04A'/><g stroke='#F7A04A' stroke-width='2' stroke-linecap='round'><path d='M12 5v3M5 8l2 2M19 8l-2 2M3 13h2M19 13h2M4 19h16'/></g></svg>",
    "__ICO_SPARK__": f"<svg {NS} viewBox='0 0 24 24'><path d='M12 2l2.2 7.8L22 12l-7.8 2.2L12 22l-2.2-7.8L2 12l7.8-2.2z' fill='#F28C28'/></svg>",
    "__ICO_CAP__": f"<svg {NS} viewBox='0 0 24 24'><path d='M12 4L1 9l11 5 9-4.1V15h2V9z' fill='#E6EEFC'/><path d='M5 12.5V16c0 1.5 3.1 3 7 3s7-1.5 7-3v-3.5L12 16z' fill='#B9CCEB'/></svg>",
    "__WAVE_SIDE__": f"<svg {NS} viewBox='0 0 320 160' preserveAspectRatio='none'><path d='M0 70 C90 20 170 120 320 55 L320 160 L0 160Z' fill='#F28C28'/><path d='M0 92 C100 52 190 140 320 80 L320 160 L0 160Z' fill='#1247B8'/></svg>",
    "__WAVE_HERO__": f"<svg {NS} viewBox='0 0 300 110' preserveAspectRatio='none'><path d='M0 110 C90 100 200 80 300 20 L300 110Z' fill='#BBD6FA'/><path d='M40 110 C130 104 220 90 300 48 L300 110Z' fill='#2F8CFF'/></svg>",
}

# ---------------------------------------------------------------
# 3) Los estilos CSS (colores, formas y letras de la página)
# ---------------------------------------------------------------
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');

:root { --logo: url("__LOGO__"); }

/* ----- Se ocultan elementos de Streamlit que no se necesitan ----- */
footer {visibility: hidden;}
[data-testid="stToolbar"] {visibility: hidden;}
[data-testid="stHeader"] {background: transparent;}

/* ----- Fondo claro y ancho de la página ----- */
[data-testid="stAppViewContainer"] {background: #F4F7FB;}
[data-testid="stMainBlockContainer"], .block-container {
    max-width: 940px;
    padding-top: 1.2rem;
}
.stMarkdown p, .stMarkdown li, [data-testid="stChatInput"] textarea,
[data-testid="stSidebar"] .stMarkdown, .stButton button p {
    font-family: 'Poppins', sans-serif;
}

/* ----- Íconos dibujados con CSS ----- */
.ico {display: inline-block; width: 18px; height: 18px; vertical-align: -3px;
      margin-right: 9px; background-size: contain; background-repeat: no-repeat;
      background-position: center;}
.ico-doc {background-image: url("__ICO_DOC__");}
.ico-shield {background-image: url("__ICO_SHIELD__");}
.ico-chat {background-image: url("__ICO_CHAT__");}
.ico-sun {background-image: url("__ICO_SUN__"); width: 22px; height: 22px; margin: 0 10px 0 0;}
.ico-spark {background-image: url("__ICO_SPARK__"); width: 15px; height: 15px; margin-right: 8px; vertical-align: -2px;}
.ico-cap {background-image: url("__ICO_CAP__"); width: 36px; height: 36px; margin: 0; flex: none;}

/* ----- Frase superior ----- */
.tagline {display: flex; align-items: center; justify-content: flex-end; gap: 10px;
          margin: 0 4px 10px 0; font-family: 'Poppins', sans-serif; font-size: 13px;}
.tagline em {color: #1B3A6B; font-style: italic;}
.tagline .ln {width: 26px; height: 2px; background: #F7A04A; border-radius: 2px;}

/* ----- Encabezado de la pantalla de inicio ----- */
/* Diseño "institucional limpio": tarjeta blanca, sin brillos ni marca de agua,
   con una franja naranja arriba como detalle de la marca */
.hero {
    position: relative; overflow: hidden; display: flex; flex-wrap: wrap;
    align-items: center; gap: 26px; padding: 28px 30px; margin-bottom: 20px;
    border-radius: 18px; border: 1px solid #DCE5F2; border-top: 4px solid #F28C28;
    background: #FFFFFF;
    box-shadow: 0 2px 10px rgba(11,42,91,0.05);
}
.hero-art {display: none;}
.hero-logo {position: relative; z-index: 1; width: 92px; height: 92px; flex: none;
            border-radius: 20px;
            background: var(--logo) center / contain no-repeat;}
.hero-texto {position: relative; z-index: 1; flex: 1; min-width: 250px;}
.hero-kicker {font-family: 'Poppins', sans-serif; font-size: 11.5px; font-weight: 600;
              color: #C26A12; letter-spacing: 1.4px; margin-bottom: 6px;}
.hero-title {font-family: 'Poppins', sans-serif; font-size: 36px; font-weight: 700;
             line-height: 1.1; color: #0B2A5B !important; margin: 0 0 10px 0; padding: 0;}
.hero-title .azul {color: #1E6BFF !important;}
.hero-sub {font-family: 'Poppins', sans-serif; font-size: 15px; line-height: 1.6;
           color: #3B4F72; margin: 0 0 16px 0; max-width: 540px;}
.chip {display: inline-block; font-family: 'Poppins', sans-serif; font-size: 12.5px;
       font-weight: 500; color: #0B2A5B; padding: 6px 14px 6px 10px; margin: 0 8px 8px 0;
       border-radius: 999px; border: 1px solid #DCE5F2;
       background: #F5F8FD;}
.chip .ico {margin-right: 8px; width: 17px; height: 17px;}

/* ----- Barra lateral ----- */
[data-testid="stSidebar"] {
    background: url("__WAVE_SIDE__") bottom center / 100% 120px no-repeat, #0B2A5B;
    border-right: none;
}
/* Espacio abajo para que la ola de colores no tape el medidor de consultas */
[data-testid="stSidebarUserContent"] {padding-bottom: 40px;}
.side-foot {position: relative; z-index: 1; margin-top: 70px !important;}
.brand {display: flex; align-items: center; gap: 12px; margin: 6px 0 22px 0;
        padding-bottom: 18px; border-bottom: 1px solid rgba(255,255,255,0.10);}
.brand-logo {width: 56px; height: 56px; flex: none; border-radius: 14px;
             background: var(--logo) center / contain no-repeat;}
.brand-text {display: flex; flex-direction: column; line-height: 1.08;
             font-family: 'Poppins', sans-serif;}
.brand-text .b1 {font-size: 16px; font-weight: 700; color: #FFFFFF; letter-spacing: 0.4px;}
.brand-text .b2 {font-size: 20px; font-weight: 700; color: #2F8CFF; letter-spacing: 0.4px;}
.brand-text .b3 {display: flex; align-items: center; gap: 6px; margin-top: 5px;
                 font-size: 8.5px; font-weight: 600; color: #E6EEFC; letter-spacing: 1.6px;}
.brand-text .b3::before, .brand-text .b3::after {content: ""; width: 16px; height: 2px;
                 background: #F7A04A; border-radius: 2px;}
.side-foot {display: flex; align-items: flex-start; gap: 12px; margin: 6px 0 0 0;
            font-family: 'Poppins', sans-serif;}
.side-foot .t {font-size: 15px; font-weight: 600; color: #FFFFFF; line-height: 1.3;}
.side-foot .s {font-size: 12.5px; color: #B9CCEB; line-height: 1.5; margin-top: 10px;}

/* ----- Botones del menú de navegación ----- */
[data-testid="stSidebar"] .stButton {width: 100%;}
[data-testid="stSidebar"] .stButton > button {
    width: 100%; justify-content: flex-start; padding: 12px 16px;
    border: none; border-radius: 12px; background: transparent; box-shadow: none;
    color: #E6EEFC; font-weight: 500; transition: background 0.2s ease;
}
[data-testid="stSidebar"] .stButton > button > div {justify-content: flex-start; gap: 8px;}
[data-testid="stSidebar"] .stButton > button p {color: inherit; font-size: 15px;}
[data-testid="stSidebar"] .stButton > button:hover {background: rgba(255,255,255,0.09); color: #FFFFFF;}
[data-testid="stSidebar"] .stButton > button[kind="primary"],
[data-testid="stSidebar"] .stButton > button[data-testid="stBaseButton-primary"] {
    background: rgba(255,255,255,0.12); color: #FFFFFF; box-shadow: inset 3px 0 0 #F28C28;
}
[data-testid="stSidebar"] .st-key-nueva button,
[data-testid="stSidebar"] .st-key-nueva button[data-testid="stBaseButton-secondary"] {
    border: 1px solid rgba(111,177,255,0.55); justify-content: center;
}
[data-testid="stSidebar"] hr {border-color: rgba(111,177,255,0.30) !important; margin: 14px 0;}

/* ----- Burbujas del chat ----- */
@keyframes aparecer {
    from {opacity: 0; transform: translateY(10px);}
    to {opacity: 1; transform: translateY(0);}
}
/* Respuesta del asistente: tarjeta blanca con una línea naranja a la izquierda */
[data-testid="stChatMessage"] {
    animation: aparecer 0.35s ease-out;
    background: #FFFFFF; border: 1px solid #DCE5F2; border-left: 4px solid #F28C28;
    border-radius: 14px; padding: 16px 20px; margin-bottom: 14px;
    box-shadow: 0 1px 4px rgba(11,42,91,0.04);
}
[data-testid="stChatMessage"] p, [data-testid="stChatMessage"] li {color: #14305C; line-height: 1.65;}
[data-testid="stChatMessage"] strong {color: #0B2A5B;}
/* Pregunta de la persona: burbuja azul a la derecha, más angosta */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    flex-direction: row-reverse; margin-left: auto; width: fit-content; max-width: 80%;
    background: #1E6BFF; border: none; padding: 10px 16px;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) p {
    color: #FFFFFF; font-weight: 500; text-align: right;
}
[data-testid="stChatMessageAvatarUser"] {background-color: #0B2A5B; color: #F7A04A;}

/* ----- Artículos citados: etiquetas naranjas; al tocarlas se abre el texto ----- */
[data-testid="stChatMessage"] [data-testid="stPopover"] button {
    background: #FFF4E6 !important; border: 1px solid #F3C89A !important; border-radius: 999px !important;
    padding: 4px 14px !important; min-height: 0 !important;
}
[data-testid="stChatMessage"] [data-testid="stPopover"] button p,
[data-testid="stChatMessage"] [data-testid="stPopover"] button span {color: #8A4A08 !important; font-weight: 600; font-size: 13px;}
[data-testid="stChatMessage"] [data-testid="stPopover"] button:hover {border-color: #F28C28 !important;}
[data-testid="stPopoverBody"] {max-width: 560px; background: #FFFFFF !important;
    border: 1px solid #DCE5F2; border-top: 3px solid #F28C28;}
[data-testid="stPopoverBody"] p {color: #14305C !important; font-size: 14px; line-height: 1.6;}
[data-testid="stExpander"] {
    border: 1px solid #F3C89A; border-radius: 10px; background: #FFF8F0;
}
[data-testid="stExpander"] details {border: none;}
[data-testid="stExpander"] summary {padding: 6px 12px;}
[data-testid="stExpander"] summary p {color: #8A4A08 !important; font-weight: 600; font-size: 13.5px;}
[data-testid="stExpander"] summary svg {fill: #C26A12; color: #C26A12;}
[data-testid="stExpander"] p, [data-testid="stExpander"] [data-testid="stCaptionContainer"] {color: #14305C;}
[data-testid="stExpander"] [data-testid="stExpanderDetails"] {background: #FFFFFF; border-radius: 0 0 10px 10px;}

/* ----- Preguntas sugeridas (pantalla de inicio) ----- */
.sug-titulo {font-family: 'Poppins', sans-serif; font-size: 13px; font-weight: 600;
             color: #3B4F72; margin: 4px 0 8px 2px;}
.st-key-sugerencias .stButton > button {
    justify-content: flex-start; text-align: left; padding: 12px 16px; min-height: 52px;
    background: #FFFFFF !important; border: 1px solid #DCE5F2 !important; border-radius: 12px !important;
    transition: border-color 0.2s ease, transform 0.2s ease;
}
.st-key-sugerencias .stButton > button > div {justify-content: flex-start; width: 100%;}
.st-key-sugerencias .stButton > button p {color: #0B2A5B !important; font-size: 14px; text-align: left;}
.st-key-sugerencias .stButton > button:hover {border-color: #F28C28 !important; transform: translateY(-1px);}

/* ----- Páginas internas (Reglamento, Historial) ----- */
.card {background: #FFFFFF; border: 1px solid #D5E5FA; border-radius: 16px;
       padding: 22px 26px; margin-bottom: 16px; font-family: 'Poppins', sans-serif;
       box-shadow: 0 1px 4px rgba(11,42,91,0.04);}
.card h3 {font-size: 18px; font-weight: 600; color: #0B1F3A; margin: 0 0 10px 0; padding: 0;}
.card p, .card li {font-size: 14px; color: #2B4670; line-height: 1.6;}
.card ul {margin: 0; padding-left: 20px;}
.paso {display: flex; align-items: flex-start; gap: 12px; margin-bottom: 12px;
       font-size: 14px; color: #2B4670; line-height: 1.45;}
.paso .num {flex: none; width: 26px; height: 26px; border-radius: 50%;
            background: #0B2A5B; color: #FFFFFF;
            font-weight: 600; font-size: 12px; display: flex; align-items: center;
            justify-content: center;}
.pagina-titulo {font-family: 'Poppins', sans-serif; font-size: 30px; font-weight: 700;
                color: #0B1F3A; margin: 4px 0 18px 0;}
.vacio {font-family: 'Poppins', sans-serif; color: #5B7399; font-size: 14px;}

/* ----- Cuadro donde se escribe la pregunta ----- */
[data-testid="stBottom"] > div, [data-testid="stBottomBlockContainer"] {background: transparent;}
[data-testid="stChatInput"] {
    border-radius: 16px; border: 1px solid #C9D7EC; background: #FFFFFF;
    box-shadow: 0 4px 16px rgba(11,42,91,0.07); transition: box-shadow 0.25s ease;
}
[data-testid="stChatInput"] > div {background: transparent;}

[data-testid="stChatInput"] textarea {color: #14305C;}
[data-testid="stChatInput"] textarea::placeholder {color: #6F86AB;}
[data-testid="stChatInput"]:focus-within {
    border-color: #4DA3FF; box-shadow: 0 0 0 3px rgba(77,163,255,0.25);
}
[data-testid="stChatInputSubmitButton"] {
    background: #1E6BFF; color: #FFFFFF;
    border-radius: 50%;
}

/* ----- Formularios (pantalla Cartas de permiso) ----- */
[data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] label {
    color: #14305C !important; font-weight: 500;
}
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p {color: #4A648F !important;}
[data-baseweb="input"], [data-baseweb="base-input"], [data-baseweb="textarea"],
[data-baseweb="select"] > div, [data-testid="stTextInputRootElement"],
[data-testid="stTextAreaRootElement"], [data-testid="stDateInputField"] {
    background-color: #FFFFFF !important; border: 1px solid #C9DCF7 !important;
    border-radius: 10px !important;
}
[data-testid="stMain"] input, [data-testid="stMain"] textarea {
    background-color: #FFFFFF !important; color: #14305C !important;
    -webkit-text-fill-color: #14305C !important;
}
/* Fecha: Streamlit dibuja día/mes/año como textos sueltos; sin esto salían blancos sobre blanco */
[data-testid="stDateInput"] [role="spinbutton"] {color: #14305C !important;}
[data-testid="stDateInput"] [data-testid="stDateInputField"] span:not([role="spinbutton"]) {color: #7F95B8 !important;}
[data-testid="stDateInput"] [role="spinbutton"]:focus {background: #E3EEFF !important; outline: none;}
/* Hora: el tema oscuro la pintaba azul marino; se iguala a los demás campos */
[data-testid="stTimeInputTimeDisplay"] {
    background-color: #FFFFFF !important; color: #14305C !important;
    border: 1px solid #C9DCF7 !important; border-radius: 10px !important;
}
[data-testid="stTimeInputTimeDisplay"] * {color: #14305C !important;}
[data-baseweb="select"] div {color: #14305C !important;}
[data-baseweb="select"] svg {fill: #14305C !important;}
[data-testid="stMain"] input::placeholder, [data-testid="stMain"] textarea::placeholder,
[data-baseweb="select"] [aria-live] {color: #7F95B8 !important; -webkit-text-fill-color: #7F95B8 !important;}
/* Lista que se abre al elegir una opción */
[data-baseweb="popover"] [data-baseweb="menu"], [data-baseweb="popover"] ul {
    background-color: #FFFFFF !important;
}
[data-baseweb="popover"] li, [data-baseweb="popover"] li * {color: #14305C !important;}
[data-baseweb="popover"] li:hover {background-color: #E3EEFA !important;}
[data-testid="stForm"] {
    background: #FFFFFF; border: 1px solid #D5E5FA; border-radius: 16px;
    box-shadow: 0 1px 4px rgba(11,42,91,0.04);
}
[data-testid="stFormSubmitButton"] button, [data-testid="stDownloadButton"] button {
    border: none; border-radius: 12px; color: #FFFFFF; font-weight: 600;
    background: #1E6BFF;
}
[data-testid="stMain"] .stButton > button {
    background: #FFFFFF; color: #14305C; border: 1px solid #C9DCF7; border-radius: 12px;
}

/* ----- Cuadros de aviso (cartas de permiso) ----- */
.aviso {font-family: 'Poppins', sans-serif; font-size: 14px; line-height: 1.55;
        padding: 14px 18px; margin: 8px 0 12px 0; border-radius: 12px;
        border: 1px solid; border-left-width: 5px;}
.aviso-info {background: #E6F0FF; border-color: #7FAEF5; color: #0B2A5B;}
.aviso-ok {background: #E4F6EA; border-color: #6CC48E; color: #0F4D2B;}
.aviso-alerta {background: #FFF3DC; border-color: #F2B24D; color: #5A3A00;}
.aviso-error {background: #FDE7E7; border-color: #E58A8A; color: #7A1C1C;}
.aviso ul {margin: 6px 0 0 0; padding-left: 20px;}
.aviso li {color: inherit; font-size: 14px; margin: 2px 0;}

/* ----- Medidor de consultas de Gemini (barra lateral) ----- */
.medidor {font-family: 'Poppins', sans-serif; margin: 16px 0 8px 0;}
.medidor-fila {display: flex; justify-content: space-between; font-size: 12.5px;
               color: #E6EEFC; margin-bottom: 6px;}
.medidor-fila b {color: #FFFFFF; font-weight: 600;}
.medidor-barra {height: 8px; background: rgba(255,255,255,0.18); border-radius: 99px; overflow: hidden;}
.medidor-relleno {height: 100%; border-radius: 99px; transition: width 0.4s ease;}
.medidor-pie {font-size: 11.5px; color: #9FB6DB; margin-top: 6px;}
[data-testid="stSidebar"] .aviso {font-size: 12.5px; padding: 10px 12px; margin: 6px 0;}

/* ----- Se ocultan los textos en inglés de Streamlit (Deploy, Rerun, etc.) ----- */
[data-testid="stToolbarActions"], [data-testid="stAppDeployButton"], [data-testid="stMainMenu"],
[data-testid="stStatusWidget"], [data-testid="stDecoration"], .stDeployButton {display: none !important;}
[data-testid="InputInstructions"] {display: none !important;}

/* ----- Pantalla de carga (se ve mientras se prepara el asistente) ----- */
.carga {
    position: fixed; inset: 0; z-index: 1000000;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    background: #F4F7FB; font-family: 'Poppins', sans-serif; text-align: center; padding: 24px;
}
.carga-logo {position: relative; width: 112px; height: 112px; margin-bottom: 26px;}
.carga-logo::before {
    content: ""; position: absolute; inset: 0; border-radius: 26px;
    background: var(--logo) center / contain no-repeat;
    animation: flotar 2.4s ease-in-out infinite;
}
.carga-logo::after {   /* anillo naranja que late alrededor del logo */
    content: ""; position: absolute; inset: -10px; border-radius: 32px;
    border: 3px solid #F28C28; opacity: 0;
    animation: latido 2.4s ease-out infinite;
}
.carga-titulo {font-size: 26px; font-weight: 700; color: #0B2A5B; line-height: 1.2; margin: 0;}
.carga-titulo span {color: #1E6BFF;}
.carga-sub {font-size: 14px; color: #5A6F94; margin: 8px 0 22px 0;}
.carga-sub::after {content: ""; animation: puntos 1.5s steps(4) infinite;}
.carga-barra {width: 220px; height: 6px; border-radius: 99px; background: #DCE5F2; overflow: hidden;}
.carga-barra div {width: 40%; height: 100%; border-radius: 99px; background: #F28C28;
                  animation: deslizar 1.3s ease-in-out infinite;}
.carga-pie {position: absolute; bottom: 26px; font-size: 12px; color: #8A9AB5;}
@keyframes flotar {0%, 100% {transform: translateY(0);} 50% {transform: translateY(-6px);}}
@keyframes latido {0% {transform: scale(0.9); opacity: 0.7;} 100% {transform: scale(1.18); opacity: 0;}}
@keyframes deslizar {0% {transform: translateX(-110%);} 100% {transform: translateX(260%);}}
@keyframes puntos {0% {content: "";} 25% {content: ".";} 50% {content: "..";} 75% {content: "...";}}

/* ----- Abrir y cerrar la barra lateral ----- */
@media (min-width: 800px) {
    [data-testid="stSidebarCollapseButton"] {display: none !important;}  /* en la computadora siempre queda abierta */
}
[data-testid="stExpandSidebarButton"], [data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"] {
    visibility: visible !important; opacity: 1 !important;
    background: #0B2A5B !important; border-radius: 10px !important;
}
[data-testid="stExpandSidebarButton"] *, [data-testid="stSidebarCollapsedControl"] *,
[data-testid="collapsedControl"] * {color: #FFFFFF !important; fill: #FFFFFF !important;}
</style>
"""


# ---------------------------------------------------------------
# 4) La pantalla de carga (la usa app.py mientras se prepara el asistente)
# ---------------------------------------------------------------
PANTALLA_CARGA = (
    '<div class="carga">'
    '<div class="carga-logo"></div>'
    '<p class="carga-titulo">Asistente del <span>Reglamento</span></p>'
    '<p class="carga-sub">Preparando el reglamento</p>'
    '<div class="carga-barra"><div></div></div>'
    f'<div class="carga-pie">{NOMBRE_APP}</div>'
    "</div>"
)


# ---------------------------------------------------------------
# 5) La función principal: aplicar los estilos a la página
# ---------------------------------------------------------------
def aplicar_estilos():
    # Se pone el logo y los íconos dentro del CSS y se inyecta en la página
    css = CSS.replace("__LOGO__", logo_uri(LOGO) if HAY_LOGO else "")
    for clave, svg in ICONOS.items():
        css = css.replace(clave, svg_uri(svg))
    st.markdown(css, unsafe_allow_html=True)