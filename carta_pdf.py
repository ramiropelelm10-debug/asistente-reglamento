# =====================================================================
# PARTE 7 de 7: ARMAR LA CARTA EN PDF                (archivo: carta_pdf.py)
# Responsable: [nombre del integrante 7]
#
# Qué hace este archivo:
#   Recibe los datos que escribió la persona y arma la carta de permiso
#   en un PDF tamaño carta, con la librería ReportLab.
#   La carta incluye: encabezado, título con el artículo del reglamento,
#   el texto con los datos, el motivo, el aviso de que NO es una
#   autorización, las firmas y el recuadro de decisión del colegio.
#
# La función principal es generar_pdf(t, datos). La usa cartas.py.
# Los datos no se guardan en ningún archivo ni se envían a la inteligencia artificial.
# =====================================================================
from datetime import date
from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import KeepInFrame, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.platypus.flowables import HRFlowable

# ---------------------------------------------------------------
# 1) Colores y límites de largo
# ---------------------------------------------------------------
AZUL = colors.HexColor("#0B2A5B")
NARANJA = colors.HexColor("#F28C28")
GRIS = colors.HexColor("#5A6F94")

MAX_TEXTO = 60     # largo máximo de los campos cortos (nombre, curso, etc.)
MAX_MOTIVO = 400   # largo máximo del motivo
MAX_CI = 15        # largo máximo del C.I.
MAX_LINEAS = 6     # renglones máximos del motivo
# Con estos límites, la carta siempre cabe en una sola hoja.


# ---------------------------------------------------------------
# 2) Estilo de los textos
# ---------------------------------------------------------------
def _estilo(nombre, **kw):
    """Crea un estilo de texto (letra, tamaño, color). kw cambia lo que haga falta."""
    base = dict(fontName="Helvetica", fontSize=11, leading=17, textColor=AZUL)
    base.update(kw)
    return ParagraphStyle(nombre, **base)


# ---------------------------------------------------------------
# 3) La función principal: armar el PDF
# ---------------------------------------------------------------
def generar_pdf(t, datos):
    """t = tipo de carta (diccionario de cartas.py). datos = lo que escribió la persona.
    Devuelve los bytes del PDF. No guarda nada en disco."""

    def v(clave):
        """Devuelve el dato escrito, sin símbolos peligrosos y con el largo limitado.
        Si está vacío, deja una línea para escribir a mano."""
        limite = {"motivo": MAX_MOTIVO, "ci": MAX_CI}.get(clave, MAX_TEXTO)
        texto = (datos.get(clave) or "").strip()[:limite]
        return escape(texto) or "________________"

    # Estilos que se usan en la carta
    marca = _estilo("marca", fontName="Helvetica-Bold", fontSize=15, leading=18)
    titulo = _estilo("titulo", fontName="Helvetica-Bold", fontSize=17, leading=22, alignment=1, spaceBefore=6)
    sub = _estilo("sub", fontSize=10, alignment=1, textColor=GRIS, spaceAfter=18)
    cuerpo = _estilo("cuerpo", leading=19, spaceAfter=10)
    chica = _estilo("chica", fontSize=9, leading=13, textColor=GRIS)
    celda = _estilo("celda", fontSize=10, leading=14, alignment=1)

    # Datos que se escriben en negrita dentro del texto de la carta
    valores = {k: f"<b>{v(k)}</b>" for k in
               ["estudiante", "curso"] + [c[0] for c in t["campos"] if c[2] != "area"]}

    # ---- Parte de arriba: encabezado, título y texto principal ----
    story = [
        Paragraph('ASISTENTE DEL <font color="#1E6BFF">REGLAMENTO</font>', marca),
        HRFlowable(width="100%", thickness=3, color=NARANJA, spaceBefore=6, spaceAfter=20),
        Paragraph(f"Señor(a) Director(a)<br/>{v('unidad')}", _estilo("dest", spaceAfter=4)),
        Paragraph(f"Fecha: {date.today().strftime('%d/%m/%Y')}", _estilo("fecha", alignment=2, spaceAfter=10)),
        Paragraph(t["titulo"], titulo),
        Paragraph(f"Según el artículo {t['articulo']} del reglamento interno", sub),
        Paragraph(f"Yo, <b>{v('tutor')}</b>, padre, madre o tutor del estudiante, "
                  + t["texto"][0].lower() + t["texto"][1:].format(**valores), cuerpo),
    ]

    # ---- Recuadro del motivo (solo si el tipo de carta tiene motivo) ----
    motivo = next((c for c in t["campos"] if c[2] == "area"), None)
    if motivo:
        # Se aceptan como máximo MAX_LINEAS renglones; los demás se juntan en el último.
        # (Muchos saltos de línea seguidos rompían el PDF o lo pasaban a otra hoja.)
        renglones = [r.strip() for r in v(motivo[0]).splitlines() if r.strip()]
        renglones = renglones[: MAX_LINEAS - 1] + [" ".join(renglones[MAX_LINEAS - 1:])]
        texto = "<br/>".join(r for r in renglones if r)
        caja = Table([[Paragraph(texto, _estilo("motivo", leading=16))]], colWidths=[6.6 * inch])
        caja.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#B7CBEB")),
                                  ("TOPPADDING", (0, 0), (-1, -1), 12), ("BOTTOMPADDING", (0, 0), (-1, -1), 24),
                                  ("LEFTPADDING", (0, 0), (-1, -1), 12)]))
        story += [caja, Spacer(1, 14)]

    # ---- Aviso: la carta no es una autorización ----
    story += [
        Paragraph("Esta carta no es una autorización. Debe entregarse firmada en regencia o en la "
                  "Dirección, que decide si la acepta.", _estilo("aviso", fontName="Helvetica-Bold",
                                                                 fontSize=10, leading=14, textColor=colors.HexColor("#B35A00"))),
        Spacer(1, 36),
    ]

    # ---- Firmas: a la izquierda el padre/madre/tutor, a la derecha el colegio ----
    firmas = Table(
        [[Paragraph(f"Firma del padre, madre o tutor<br/>C.I.: {v('ci')}", celda), "",
          Paragraph("Decisión del colegio<br/>[&nbsp;&nbsp;&nbsp;] Aceptada &nbsp;&nbsp;&nbsp; [&nbsp;&nbsp;&nbsp;] No aceptada<br/>"
                    "Sello y firma de regencia o Dirección", celda)]],
        colWidths=[3.0 * inch, 0.6 * inch, 3.0 * inch])
    firmas.setStyle(TableStyle([("LINEABOVE", (0, 0), (0, 0), 1, AZUL), ("LINEABOVE", (2, 0), (2, 0), 1, AZUL),
                                ("TOPPADDING", (0, 0), (-1, -1), 8), ("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story += [firmas, Spacer(1, 24),
              Paragraph("Documento preparado con el Asistente del Reglamento. Los datos no se guardan.", chica)]

    # ---- Armar el PDF en la memoria y devolver sus bytes ----
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter, leftMargin=0.95 * inch, rightMargin=0.95 * inch,
                            topMargin=0.8 * inch, bottomMargin=0.8 * inch, title=t["titulo"])
    # KeepInFrame achica un poco todo el contenido si no cabe, así la carta siempre sale en UNA hoja
    # (el marco de la hoja tiene 6 puntos de relleno a cada lado; por eso se restan 12).
    hoja = KeepInFrame(doc.width - 12, doc.height - 12, story, mode="shrink")
    doc.build([hoja])
    return buf.getvalue()