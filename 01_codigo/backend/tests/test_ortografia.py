"""
Tests de ortografía (Cambio A)
==============================
A1 – Comprueba que no existan palabras sin tilde en los textos visibles de los
     archivos .html y .js del frontend.
A2 – Comprueba que los HTTPException detail strings del backend no contengan
     palabras sin tilde.
A3 – Comprueba que i18n.js exista y que todas sus claves coincidan con las
     referencias data-i18n del HTML.  (Ejecutado tras Cambio B.)
"""
import re
import pathlib

# ── Rutas ─────────────────────────────────────────────────────────────────────
ROOT = pathlib.Path(__file__).resolve().parents[3]          # raíz del repo
FRONTEND_JS   = ROOT / "01_codigo" / "frontend" / "static" / "js"
FRONTEND_HTML = ROOT / "01_codigo" / "frontend" / "templates"
BACKEND_API   = ROOT / "01_codigo" / "backend" / "app" / "api"

# ── Errores conocidos (incorrecto → correcto) ──────────────────────────────────
# Solo palabras que deben llevar tilde según RAE y aparecían en la app.
ERRORES_CONOCIDOS = [
    # Verbos / adjetivos comunes
    (r"\bInicia sesion\b",       "Inicia sesión"),
    (r"\binicia sesion\b",       "inicia sesión"),
    # máquina y derivados
    (r"\besta maquina\b",        "esta máquina"),
    (r"\bla maquina\b",          "la máquina"),
    (r"\buna maquina\b",         "una máquina"),
    (r"\bde maquina\b",          "de máquina"),
    (r"\bsu maquina\b",          "su máquina"),
    (r"\btu maquina\b",          "tu máquina"),
    (r"\b(\d+) maquina\b",       r"\1 máquina"),   # "3 maquinas"
    # ubicación
    (r"\bUbicar?cion\b",         "Ubicación"),
    (r"\bubicar?cion\b",         "ubicación"),
    # teléfono
    (r"\bTelefono\b",            "Teléfono"),
    (r"\btelefono\b",            "teléfono"),
    # descripción
    (r"\bDescripcion\b",         "Descripción"),
    (r"\bdescripcion\b",         "descripción"),
    # gestión / búsqueda / publicación
    (r"\bGestion\b",             "Gestión"),
    (r"\bgestion\b",             "gestión"),
    (r"\bBusqueda\b",            "Búsqueda"),
    (r"\bbusqueda\b",            "búsqueda"),
    (r"\bPublicacion\b",         "Publicación"),
    (r"\bpublicacion\b",         "publicación"),
    # adverbios / pronombres
    (r"\btodavia\b",             "todavía"),
    (r"\baun\b",                 "aún"),   # solo cuando significa «todavía»
    # otros
    (r"\bperiodo\b",             "período"),   # uso técnico con tilde
    (r"\bpublico\b",             "público"),
    (r"\bdía\b",                 None),         # referencia positiva — debe existir en vez de /dia
    (r"\b/dia\b",                "/día"),
    (r"\bGrua\b",                "Grúa"),
    (r"\bCamion\b",              "Camión"),
    (r"\bExcavacion\b",          "Excavación"),
    (r"\bCompactacion\b",        "Compactación"),
    (r"\bElevacion\b",           "Elevación"),
    (r"\bDemolicion\b",          "Demolición"),
]

# Patrones que deben NO aparecer (incorrecto)
PATRONES_ERRONEOS = [
    (r"\bInicia sesion\b",   "Inicia sesión"),
    (r"\besta maquina\b",    "esta máquina"),
    (r"\bUbicar?cion\b",     "Ubicación"),
    (r"\bubicar?cion\b",     "ubicación"),
    (r"\bTelefono\b",        "Teléfono"),
    (r"\bdescripcion\b",     "descripción"),
    (r"\bDescripcion\b",     "Descripción"),
    (r"\bGestion\b",         "Gestión"),
    (r"\bbusqueda\b",        "búsqueda"),
    (r"\bBusqueda\b",        "Búsqueda"),
    (r"\bpublicacion\b",     "publicación"),
    (r"\bPublicacion\b",     "Publicación"),
    (r"\btodavia\b",         "todavía"),
    (r"\bperiodo\b",         "período"),
    (r"\bpublico\b",         "público"),
    (r"\b/dia\b",            "/día"),
    (r"\bGrua Torre\b",      "Grúa Torre"),
    (r"\bCamion Grua\b",     "Camión Grúa"),
]


def collect_files(directory: pathlib.Path, suffixes):
    """Devuelve todos los archivos con las extensiones indicadas bajo directory."""
    files = []
    for suffix in suffixes:
        files.extend(directory.rglob(f"*{suffix}"))
    return files


def find_pattern_in_files(pattern: str, files) -> list[tuple]:
    """
    Devuelve lista de (ruta, número_línea, línea) donde aparece el patrón.
    Ignora líneas que son comentarios puros (empiezan con # o //).
    """
    rx = re.compile(pattern, re.IGNORECASE)
    hits = []
    for f in files:
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            stripped = line.strip()
            # Saltar líneas de comentario puro (no afectan al usuario)
            if stripped.startswith("//") or stripped.startswith("#") or stripped.startswith("*"):
                continue
            if rx.search(line):
                hits.append((str(f), lineno, line.strip()))
    return hits


# ─────────────────────────────────────────────────────────────────────────────
# A1 – Frontend: archivos .html y .js
# ─────────────────────────────────────────────────────────────────────────────

def test_A1_no_tildes_faltantes_html_js():
    """
    Ningún archivo HTML o JS del frontend debe contener los patrones erróneos
    en texto visible (se excluyen líneas de comentario puro e i18n.js,
    que contiene texto multiidioma donde las reglas RAE españolas no aplican
    a los bloques catalán/inglés).
    """
    js_files   = collect_files(FRONTEND_JS,   [".js"])
    html_files = collect_files(FRONTEND_HTML, [".html"])
    # Excluir i18n.js: contiene traducciones en CA/EN donde las reglas RAE
    # del español no aplican (p. ej. "dia" es correcto en catalán).
    js_files = [f for f in js_files if f.name != 'i18n.js']
    all_files  = js_files + html_files

    errores = []
    for patron, correcto in PATRONES_ERRONEOS:
        hits = find_pattern_in_files(patron, all_files)
        for (ruta, lineno, linea) in hits:
            errores.append(
                f"[{ruta}:{lineno}] Patrón «{patron}» → debería ser «{correcto}»\n  Línea: {linea}"
            )

    assert not errores, (
        f"\n{len(errores)} error(es) ortográfico(s) encontrado(s):\n\n"
        + "\n".join(errores)
    )


# ─────────────────────────────────────────────────────────────────────────────
# A2 – Backend: strings en HTTPException(detail=...)
# ─────────────────────────────────────────────────────────────────────────────

# Patrones a comprobar en detail strings del backend (los mismos relevantes)
PATRONES_BACKEND = [
    (r"esta maquina",   "esta máquina"),
    (r"ubicacion",      "ubicación"),
    (r"telefono",       "teléfono"),
    (r"descripcion",    "descripción"),
    (r"gestion",        "gestión"),
    (r"busqueda",       "búsqueda"),
    (r"todavia",        "todavía"),
]


def test_A2_no_tildes_faltantes_backend_exceptions():
    """
    Los HTTPException(detail=...) del backend no deben contener palabras
    sin tilde.  Solo se analiza el contenido de los strings detail=, no
    comentarios ni docstrings.
    """
    py_files = collect_files(BACKEND_API, [".py"])
    # Regex para capturar el contenido del parámetro detail=
    detail_rx = re.compile(r'detail\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)

    errores = []
    for f in py_files:
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            m = detail_rx.search(line)
            if not m:
                continue
            detail_str = m.group(1)
            for patron, correcto in PATRONES_BACKEND:
                if re.search(patron, detail_str, re.IGNORECASE):
                    errores.append(
                        f"[{f}:{lineno}] detail contiene «{patron}» → «{correcto}»\n  {line.strip()}"
                    )

    assert not errores, (
        f"\n{len(errores)} error(es) en detail de HTTPException:\n\n"
        + "\n".join(errores)
    )


# ─────────────────────────────────────────────────────────────────────────────
# A3 – Consistencia i18n (se activa cuando i18n.js existe)
# ─────────────────────────────────────────────────────────────────────────────

def test_A3_i18n_key_consistency():
    """
    Si i18n.js existe:
      • Extrae todas las claves del objeto TRANSLATIONS (primer nivel de 'es').
      • Extrae todas las referencias data-i18n="key" del HTML.
      • Verifica que cada clave data-i18n esté definida en TRANSLATIONS['es'].
    Si i18n.js no existe aún, el test se salta automáticamente.
    """
    import pytest

    i18n_path = FRONTEND_JS / "i18n.js"
    if not i18n_path.exists():
        pytest.skip("i18n.js no existe todavía (se creará en Cambio B)")

    # Extraer claves de TRANSLATIONS.es  ── bloque es: { … } (con o sin comillas)
    i18n_text = i18n_path.read_text(encoding="utf-8")
    # Buscar 'es': {  o  "es": {  o  es: {
    start_rx = re.compile(r"""(?:['"]es['"]\s*|(?<!['\"\w])es\s*):\s*\{""")
    m_start = start_rx.search(i18n_text)
    assert m_start, "No se encontró el bloque 'es' en TRANSLATIONS de i18n.js"

    # Extraer bloque balanceado
    brace_start = i18n_text.index('{', m_start.start())
    depth = 0
    i = brace_start
    while i < len(i18n_text):
        if i18n_text[i] == '{':
            depth += 1
        elif i18n_text[i] == '}':
            depth -= 1
            if depth == 0:
                break
        i += 1
    es_block = i18n_text[brace_start:i+1]

    key_rx = re.compile(r"""(?:['"]([\w]+)['"]\s*:|(\b[\w]+\b)\s*:)""")
    i18n_keys = set()
    for km in key_rx.finditer(es_block):
        k = km.group(1) or km.group(2)
        if k:
            i18n_keys.add(k)

    # Extraer referencias data-i18n del HTML
    html_files = collect_files(FRONTEND_HTML, [".html"])
    data_i18n_rx = re.compile(r'data-i18n=["\']([^"\']+)["\']')
    html_refs = set()
    for hf in html_files:
        html_refs.update(data_i18n_rx.findall(hf.read_text(encoding="utf-8")))

    # Toda referencia HTML debe tener clave en i18n.js
    missing = html_refs - i18n_keys
    assert not missing, (
        f"Claves data-i18n sin definición en TRANSLATIONS['es']: {sorted(missing)}"
    )
