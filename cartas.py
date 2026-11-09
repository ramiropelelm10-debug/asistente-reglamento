# =====================================================================
# PARTE 6 de 7: LAS CARTAS DE PERMISO                    (archivo: cartas.py)
# Responsable: [nombre del integrante 6]
#
# Qué hace este archivo:
#   1. Define los 4 tipos de carta (TIPOS): salida anticipada, justificación
#      de inasistencia, permiso prolongado y medicamentos. Cada uno tiene su
#      artículo del reglamento, sus campos y su texto.
#   2. Dibuja la pantalla "Cartas de permiso": lista de tipos, formulario
#      y botón de descarga.
#   3. Revisa los datos (que no falte nada, que las fechas tengan sentido).
#      El curso y el paralelo se eligen en menús desplegables.
#   4. Llama a generar_pdf (carta_pdf.py) para armar el PDF.
#
# Importante: el asistente solo PREPARA la carta. El colegio decide.
# =====================================================================
from datetime import date, time
from html import escape

import streamlit as st

from carta_pdf import MAX_CI, MAX_MOTIVO, MAX_TEXTO, generar_pdf
from validar import limites_fecha, revisar

# ---------------------------------------------------------------
# 1) Los tipos de carta
#    Cada campo es (clave, etiqueta, tipo). Tipos: "texto", "fecha", "hora", "area".
#    En "texto" se escribe {nombre} para que el programa ponga el dato.
# ---------------------------------------------------------------
TIPOS = {
    "Salida anticipada": {
        "archivo": "salida_anticipada",
        "articulo": "26",
        "titulo": "CARTA DE SALIDA ANTICIPADA",
        "campos": [("fecha", "Fecha de la salida", "fecha"),
                   ("hora", "Hora de salida", "hora"),
                   ("motivo", "Motivo", "area")],
        "texto": "Solicito que se permita la salida anticipada del estudiante {estudiante}, del curso "
                 "{curso}, el día {fecha} a las {hora}. El motivo es el siguiente:",
        "nota": "Artículo 26: la salida se registra en regencia, y el estudiante debe ser recogido por su "
                "padre, madre o tutor, o contar con una autorización escrita.",
    },
    "Justificación de inasistencia": {
        "archivo": "justificacion_inasistencia",
        "articulo": "22",
        "titulo": "CARTA DE JUSTIFICACIÓN DE INASISTENCIA",
        "campos": [("desde", "Primer día de falta", "fecha"),
                   ("hasta", "Último día de falta", "fecha"),
                   ("motivo", "Motivo", "area")],
        "texto": "Justifico la inasistencia del estudiante {estudiante}, del curso {curso}, desde el "
                 "{desde} hasta el {hasta}. El motivo fue el siguiente:",
        "nota": "Artículos 22 y 23: se entrega por escrito, firmada, dentro de los 3 días hábiles "
                "posteriores a la falta. Si la ausencia por enfermedad pasó de 2 días seguidos, adjunte "
                "un certificado médico.",
    },
    "Permiso prolongado": {
        "archivo": "permiso_prolongado",
        "articulo": "27",
        "titulo": "SOLICITUD DE PERMISO PROLONGADO",
        "campos": [("desde", "Fecha de salida", "fecha"),
                   ("hasta", "Fecha de retorno", "fecha"),
                   ("motivo", "Motivo (por ejemplo, un viaje familiar)", "area")],
        "texto": "Solicito un permiso de ausencia para el estudiante {estudiante}, del curso {curso}, "
                 "desde el {desde} hasta el {hasta}. El motivo es el siguiente:",
        "nota": "Artículo 27: la solicitud se presenta a la Dirección con al menos 5 días de anticipación.",
    },
    "Medicamentos en el colegio": {
        "archivo": "medicamentos",
        "articulo": "66",
        "titulo": "AUTORIZACIÓN PARA MEDICAMENTOS",
        "campos": [("medicamento", "Nombre del medicamento", "texto"),
                   ("dosis", "Dosis y horario", "texto"),
                   ("duracion", "Duración del tratamiento", "texto")],
        "texto": "Solicito que al estudiante {estudiante}, del curso {curso}, se le administre en la "
                 "unidad educativa el siguiente medicamento: {medicamento}. Dosis y horario: {dosis}. "
                 "Duración del tratamiento: {duracion}.",
        "nota": "Artículo 66: se entrega en enfermería junto con la receta médica y esta autorización escrita.",
    },
}


# ---------------------------------------------------------------
# 2) Opciones de los menús desplegables
# ---------------------------------------------------------------
# Cursos: de 1.º de primaria a 6.º de secundaria
CURSOS = [f"{n}.º de primaria" for n in range(1, 7)] + [f"{n}.º de secundaria" for n in range(1, 7)]
PARALELOS = ["A", "B", "C", "D", "E", "F"]


def _aviso(tipo, texto):
    """Cuadro de aviso con los colores de la página.
    tipo: "info", "ok", "alerta" o "error" (los estilos están en estilos.py)."""
    st.markdown(f'<div class="aviso aviso-{tipo}">{escape(texto)}</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------
# 3) Dibujar un campo del formulario según su tipo
# ---------------------------------------------------------------
def _campo(col, etiqueta, tipo, clave, tipo_carta, campo):
    if tipo == "fecha":
        # El calendario solo deja elegir fechas con sentido (los límites están en validar.py)
        lo, hi = limites_fecha(tipo_carta, campo)
        hoy = date.today()
        inicial = min(max(hoy, lo), hi) if lo else hoy
        return col.date_input(etiqueta, value=inicial, min_value=lo, max_value=hi,
                              format="DD/MM/YYYY", key=clave)
    if tipo == "hora":
        # Reloj con pasos de 5 minutos: no se puede escribir una hora inventada
        return col.time_input(etiqueta, value=None, step=300, key=clave)
    if tipo == "area":
        return col.text_area(etiqueta, key=clave, height=110, max_chars=MAX_MOTIVO,
                             placeholder="Por ejemplo: cita médica con el pediatra a las 10:30.")
    return col.text_input(etiqueta, key=clave, max_chars=MAX_TEXTO)


# ---------------------------------------------------------------
# 4) La pantalla "Cartas de permiso" (la llama app.py)
# ---------------------------------------------------------------
def pantalla_cartas():
    st.caption("El asistente prepara la carta. Tú la imprimes, la firmas y la entregas en regencia o en la "
               "Dirección. El colegio decide si la acepta. Los datos que escribes no se envían a la "
               "inteligencia artificial ni se guardan en ningún archivo.")

    # a) Elegir el tipo de carta y mostrar lo que pide el reglamento
    tipo = st.selectbox("Tipo de carta", list(TIPOS))
    t = TIPOS[tipo]
    _aviso("info", t["nota"])

    # b) Formulario: datos comunes y datos propios de cada tipo de carta
    with st.form("form_carta"):
        c1, c2, c3 = st.columns([2.2, 1.7, 0.9])
        estudiante = c1.text_input("Nombre del estudiante", key=f"est_{tipo}", max_chars=MAX_TEXTO,
                                   placeholder="Nombre y apellidos")
        # Menús desplegables: el curso (de 1.º de primaria a 6.º de secundaria) y el paralelo
        curso = c2.selectbox("Curso", CURSOS, index=None, placeholder="Elige el curso", key=f"cur_{tipo}")
        paralelo = c3.selectbox("Paralelo", PARALELOS, index=None, placeholder="Elige", key=f"par_{tipo}")
        c4, c5 = st.columns(2)
        datos = {
            "estudiante": estudiante,
            # Si falta el curso o el paralelo, queda vacío y el programa avisa
            "curso": f"{curso} {paralelo}" if curso and paralelo else "",
            "tutor": c4.text_input("Padre, madre o tutor", key=f"tut_{tipo}", max_chars=MAX_TEXTO,
                                   placeholder="Nombre y apellidos"),
            "ci": c5.text_input("C.I. (opcional)", key=f"ci_{tipo}", max_chars=MAX_CI,
                                placeholder="1234567 LP"),
            "unidad": st.text_input("Unidad educativa (opcional)", key=f"uni_{tipo}", max_chars=MAX_TEXTO),
        }
        fechas, hora = {}, None
        for clave, etiqueta, ctipo in t["campos"]:
            valor = _campo(st, etiqueta, ctipo, f"{clave}_{tipo}", tipo, clave)
            if isinstance(valor, time):
                hora = valor
            elif isinstance(valor, date):
                fechas[clave] = valor
                datos[clave] = valor.strftime("%d/%m/%Y")
            else:
                datos[clave] = valor
        enviado = st.form_submit_button("Generar carta")

    # c) Al presionar "Generar carta": revisar los datos y armar el PDF
    if enviado:
        # validar.py revisa cada dato y lo ordena (por ejemplo, "ramiro alex" -> "Ramiro Alex")
        datos, errores = revisar(tipo, t["campos"], datos, fechas, hora)
        desde = fechas.get("desde")
        if errores:
            st.session_state.pop("carta_pdf", None)
            lista = "".join(f"<li>{escape(e)}</li>" for e in errores)
            st.markdown(f'<div class="aviso aviso-error"><b>Revisa estos datos:</b><ul>{lista}</ul></div>',
                        unsafe_allow_html=True)
        else:
            if tipo == "Permiso prolongado" and (desde - date.today()).days < 5:
                _aviso("alerta", "El artículo 27 pide presentar la solicitud con al menos 5 días de anticipación. "
                                 "La Dirección decide si la acepta.")
            st.session_state.carta_pdf = {
                "tipo": tipo,
                "bytes": generar_pdf(t, datos),
                "archivo": f"carta_{t['archivo']}.pdf",
            }

    # d) Mostrar el botón de descarga (solo de la carta del tipo elegido)
    carta = st.session_state.get("carta_pdf")
    if carta and carta["tipo"] == tipo:
        _aviso("ok", "La carta está lista. Descárgala, imprímela, fírmala y entrégala en regencia.")
        st.download_button("Descargar carta en PDF", data=carta["bytes"], file_name=carta["archivo"],
                           mime="application/pdf")
        if st.button("Hacer otra carta"):
            st.session_state.pop("carta_pdf", None)
            st.rerun()