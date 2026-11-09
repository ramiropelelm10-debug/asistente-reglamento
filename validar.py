# =====================================================================
# PARTE EXTRA: REVISAR Y ORDENAR LOS DATOS DE LAS CARTAS   (archivo: validar.py)
#
# Qué hace este archivo:
#   Antes de armar la carta en PDF, revisa cada dato que escribió la persona
#   para que no se pueda llenar con cualquier cosa rara:
#   1. Nombres (estudiante y tutor): solo letras, con nombre y apellido.
#      Además los ordena: "  ramiro   ALEX" -> "Ramiro Alex".
#   2. C.I.: solo números (5 a 10), con complemento y departamento opcionales,
#      por ejemplo "1234567", "1234567-1A" o "1234567 LP".
#   3. Unidad educativa, medicamento, dosis y duración: letras, números y
#      signos comunes. No acepta símbolos raros ni letras repetidas (aaaaa).
#   4. Motivo: al menos 10 letras y 2 palabras.
#   5. Fechas y hora: que estén dentro de lo que tiene sentido.
#
# La función principal es revisar(tipo, datos, fechas, hora). La usa cartas.py.
# Devuelve (datos ordenados, lista de errores). Si la lista está vacía, todo está bien.
# =====================================================================
import re
import unicodedata
from datetime import date, time, timedelta

LETRAS = "A-Za-zÁÉÍÓÚÜÑáéíóúüñ"

# Nombre: palabras de letras, separadas por espacio, guion o apóstrofo (María-José, D'Arcy)
RE_NOMBRE = re.compile(rf"^[{LETRAS}]+(?:['\-][{LETRAS}]+)*(?: [{LETRAS}]+(?:['\-][{LETRAS}]+)*)+$")
# C.I. boliviano: 5 a 10 números, complemento opcional (-1A) y departamento opcional (LP, CB...)
RE_CI = re.compile(r"^\d{5,10}(?:-[0-9A-Z]{1,2})?(?: (?:LP|CB|SC|OR|PT|CH|TJ|BN|PD))?$")
# Texto corto: letras, números, espacios y signos comunes
RE_TEXTO = re.compile(rf"^[{LETRAS}0-9 .,;:()\-/%°º\"'#+]+$")
# Motivo: lo mismo, más signos de pregunta y exclamación y saltos de línea
RE_MOTIVO = re.compile(rf"^[{LETRAS}0-9 .,;:()\-/%°º\"'#+¿?¡!\n]+$")
# La misma letra 4 veces o más seguidas (aaaa, xxxxx): casi siempre es texto de relleno
RE_REPETIDA = re.compile(rf"([{LETRAS}])\1{{3,}}", re.I)

# Palabras que van en minúscula dentro de un nombre (María de la Cruz)
MINUSCULAS = {"de", "del", "la", "las", "los", "y"}

# Horario en que tiene sentido pedir una salida anticipada
HORA_MIN, HORA_MAX = time(7, 0), time(19, 0)

# Fechas permitidas, en días desde hoy: (mínimo, máximo)
LIMITES_FECHA = {
    ("Salida anticipada", "fecha"): (0, 30),             # hoy o dentro de un mes
    ("Justificación de inasistencia", "desde"): (-30, 0),  # faltas del último mes
    ("Justificación de inasistencia", "hasta"): (-30, 0),
    ("Permiso prolongado", "desde"): (0, 180),           # desde hoy hasta 6 meses
    ("Permiso prolongado", "hasta"): (0, 270),
}
MAX_DIAS_PERMISO = 90   # un permiso prolongado no puede durar más de 90 días


# ---------------------------------------------------------------
# 1) Limpieza básica: quita símbolos invisibles y espacios de más
# ---------------------------------------------------------------
def limpiar(texto, saltos=False):
    """Quita caracteres invisibles o de control y junta los espacios repetidos.
    Si saltos=True, conserva los saltos de línea (para el motivo)."""
    texto = unicodedata.normalize("NFC", str(texto or ""))
    texto = "".join(c for c in texto if c == "\n" or unicodedata.category(c)[0] != "C")
    if saltos:
        lineas = [re.sub(r"[ \t]+", " ", l).strip() for l in texto.split("\n")]
        return "\n".join(l for l in lineas if l)
    return re.sub(r"\s+", " ", texto).strip()


def nombre_propio(texto):
    """'ramiro  ALEX de la cruz' -> 'Ramiro Alex de la Cruz'."""
    palabras = limpiar(texto).split(" ")
    salida = []
    for i, p in enumerate(palabras):
        if i > 0 and p.lower() in MINUSCULAS:
            salida.append(p.lower())
        else:
            # Mayúscula después de guion o apóstrofo también: maría-josé -> María-José
            salida.append(re.sub(rf"(^|['\-])([{LETRAS}])", lambda m: m.group(1) + m.group(2).upper(), p.lower()))
    return " ".join(salida)


def _letras(texto):
    return sum(c.isalpha() for c in texto)


# ---------------------------------------------------------------
# 2) Revisión de cada tipo de dato. Cada una devuelve (valor ordenado, error o None)
# ---------------------------------------------------------------
def revisar_nombre(texto, quien):
    v = nombre_propio(texto)
    if not v:
        return v, f"Escribe el nombre del {quien}."
    if not RE_NOMBRE.match(v):
        if len(v.split(" ")) < 2 and re.fullmatch(rf"[{LETRAS}'\-]+", v):
            return v, f"Escribe el nombre y al menos un apellido del {quien}."
        return v, f"El nombre del {quien} solo puede tener letras (sin números ni símbolos)."
    if RE_REPETIDA.search(v):
        return v, f"El nombre del {quien} parece incorrecto (tiene letras repetidas)."
    if any(len(p) < 2 for p in v.split(" ") if p.lower() not in MINUSCULAS):
        return v, f"Escribe el nombre del {quien} completo, sin iniciales sueltas."
    return v, None


def revisar_ci(texto):
    v = limpiar(texto).upper().replace(".", "")
    if not v:
        return v, None   # es opcional
    if not RE_CI.match(v):
        return v, "El C.I. debe tener solo números (5 a 10). Puedes agregar complemento y departamento, por ejemplo 1234567-1A LP."
    return v, None


def revisar_texto(texto, nombre, obligatorio=True, minimo=2):
    v = limpiar(texto)
    if not v:
        return v, (f"Completa el campo «{nombre}»." if obligatorio else None)
    if not RE_TEXTO.match(v):
        return v, f"«{nombre}» tiene símbolos no permitidos. Usa solo letras, números y signos comunes."
    if _letras(v) < minimo:
        return v, f"«{nombre}» es demasiado corto o no tiene letras."
    if RE_REPETIDA.search(v):
        return v, f"«{nombre}» parece texto de relleno (tiene letras repetidas)."
    return v, None


def revisar_motivo(texto):
    v = limpiar(texto, saltos=True)
    if not v:
        return v, "Escribe el motivo."
    if not RE_MOTIVO.match(v):
        return v, "El motivo tiene símbolos no permitidos. Usa solo letras, números y signos comunes."
    if _letras(v) < 10 or len(re.findall(rf"[{LETRAS}]{{2,}}", v)) < 2:
        return v, "Explica un poco más el motivo (al menos 2 palabras y 10 letras)."
    if RE_REPETIDA.search(v):
        return v, "El motivo parece texto de relleno (tiene letras repetidas)."
    return v, None


def limites_fecha(tipo, clave, hoy=None):
    """Fecha mínima y máxima permitidas para un campo de fecha (o None si no tiene límite)."""
    hoy = hoy or date.today()
    if (tipo, clave) not in LIMITES_FECHA:
        return None, None
    lo, hi = LIMITES_FECHA[(tipo, clave)]
    return hoy + timedelta(days=lo), hoy + timedelta(days=hi)


# ---------------------------------------------------------------
# 3) La función principal: revisar todo el formulario
# ---------------------------------------------------------------
def revisar(tipo, campos, datos, fechas, hora=None, hoy=None):
    """tipo = nombre del tipo de carta; campos = lista de campos de ese tipo (cartas.py).
    datos = textos escritos; fechas = {clave: date}; hora = time o None.
    Devuelve (datos ordenados, lista de errores)."""
    hoy = hoy or date.today()
    errores = []
    limpio = dict(datos)

    def anotar(clave, resultado):
        valor, error = resultado
        limpio[clave] = valor
        if error:
            errores.append(error)

    anotar("estudiante", revisar_nombre(datos.get("estudiante"), "estudiante"))
    if not datos.get("curso"):
        errores.append("Elige el curso y el paralelo.")
    anotar("tutor", revisar_nombre(datos.get("tutor"), "padre, madre o tutor"))
    anotar("ci", revisar_ci(datos.get("ci")))
    anotar("unidad", revisar_texto(datos.get("unidad"), "Unidad educativa", obligatorio=False, minimo=3))

    for clave, etiqueta, ctipo in campos:
        if ctipo == "area":
            anotar(clave, revisar_motivo(datos.get(clave)))
        elif ctipo == "texto":
            anotar(clave, revisar_texto(datos.get(clave), etiqueta))
        elif ctipo == "hora":
            if hora is None:
                errores.append("Elige la hora de salida.")
            elif not (HORA_MIN <= hora <= HORA_MAX):
                errores.append(f"La hora de salida debe estar entre las {HORA_MIN:%H:%M} y las {HORA_MAX:%H:%M}.")
            else:
                limpio[clave] = hora.strftime("%H:%M")
        elif ctipo == "fecha":
            f = fechas.get(clave)
            lo, hi = limites_fecha(tipo, clave, hoy)
            if f is None:
                errores.append(f"Elige la fecha «{etiqueta}».")
            elif lo and not (lo <= f <= hi):
                errores.append(f"«{etiqueta}» debe estar entre el {lo:%d/%m/%Y} y el {hi:%d/%m/%Y}.")

    desde, hasta = fechas.get("desde"), fechas.get("hasta")
    if desde and hasta:
        if hasta < desde:
            errores.append("La fecha final no puede ser anterior a la fecha inicial.")
        elif tipo == "Permiso prolongado" and (hasta - desde).days > MAX_DIAS_PERMISO:
            errores.append(f"El permiso prolongado no puede durar más de {MAX_DIAS_PERMISO} días.")

    return limpio, errores
