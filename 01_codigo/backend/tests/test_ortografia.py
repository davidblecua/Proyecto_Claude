"""
Tests de ortografía — Cambio A
================================
A1 – Palabras sin tilde obligatoria en .html/.js del frontend.
A2 – Mensajes de error (HTTPException detail) en routers .py del backend.
A3 – Los tres idiomas en i18n.js tienen exactamente las mismas claves.
"""
import re
import pathlib
import pytest

# ── Rutas ─────────────────────────────────────────────────────────────────────
ROOT          = pathlib.Path(__file__).resolve().parents[3]
FRONTEND_JS   = ROOT / "01_codigo" / "frontend" / "static" / "js"
FRONTEND_HTML = ROOT / "01_codigo" / "frontend" / "templates"
BACKEND_API   = ROOT / "01_codigo" / "backend" / "app" / "api"

# ── ERRORES_CONOCIDOS ─────────────────────────────────────────────────────────
ERRORES_CONOCIDOS = [
    ("maquina",     "máquina"),
    ("tecnico",     "técnico"),
    ("numero",      "número"),
    ("pagina",      "página"),
    ("publico",     "público"),
    ("busqueda",    "búsqueda"),
    ("codigo",      "código"),
    ("rapido",      "rápido"),
    ("unico",       "único"),
    ("basico",      "básico"),
    ("practico",    "práctico"),
    ("automatico",  "automático"),
    ("periodo",     "período"),
    ("modulo",      "módulo"),
    ("ultimo",      "último"),
    ("proximo",     "próximo"),
    ("tambien",     "también"),
    ("ademas",      "además"),
    ("despues",     "después"),
    ("informacion", "información"),
    ("direccion",   "dirección"),
    ("seccion",     "sección"),
    ("gestion",     "gestión"),
    ("accion",      "acción"),
    ("publicacion", "publicación"),
    ("facil",       "fácil"),
    ("util",        "útil"),
    ("movil",       "móvil"),
]


def _collect_files(directory: pathlib.Path, suffixes):
    files = []
    for suffix in suffixes:
        files.extend(directory.rglob(f"*{suffix}"))
    return files


def _is_comment_line(line: str) -> bool:
    """Devuelve True si la línea es un comentario puro (no cuenta como texto visible)."""
    s = line.strip()
    return s.startswith("//") or s.startswith("#") or s.startswith("*") or s.startswith("/*")


def _find_pattern_in_files(pattern: str, files) -> list:
    """Lista de (ruta, lineno, línea) donde aparece el patrón (excluye comentarios)."""
    rx = re.compile(rf"\b{re.escape(pattern)}\b", re.IGNORECASE)
    hits = []
    for f in files:
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            if _is_comment_line(line):
                continue
            if rx.search(line):
                hits.append((str(f), lineno, line.strip()))
    return hits


# ─────────────────────────────────────────────────────────────────────────────
# A1 – Frontend: .html y .js
# ─────────────────────────────────────────────────────────────────────────────

def test_A1_palabras_sin_tilde_html_js():
    """
    Ningún archivo HTML o JS del frontend debe contener palabras sin tilde
    obligatoria en texto visible (excluye comentarios e i18n.js, que tiene
    texto multiidioma donde las reglas RAE no aplican a CA/EN).
    """
    js_files   = _collect_files(FRONTEND_JS,   [".js"])
    html_files = _collect_files(FRONTEND_HTML, [".html"])
    # i18n.js contiene texto en CA/EN — excluid
    js_files   = [f for f in js_files if f.name != "i18n.js"]
    # Excluir también los propios archivos de test
    js_files   = [f for f in js_files if "test" not in f.name]
    all_files  = js_files + html_files

    errores = []
    for palabra, correcto in ERRORES_CONOCIDOS:
        hits = _find_pattern_in_files(palabra, all_files)
        for ruta, lineno, linea in hits:
            errores.append(
                f"[{ruta}:{lineno}] «{palabra}» → «{correcto}»\n  {linea}"
            )

    assert not errores, (
        f"\n{len(errores)} error(es) ortográfico(s):\n\n" + "\n".join(errores)
    )


# ─────────────────────────────────────────────────────────────────────────────
# A2 – Backend: strings detail= en HTTPException
# ─────────────────────────────────────────────────────────────────────────────

def test_A2_errores_en_detail_de_HTTPException():
    """
    Los strings detail= de HTTPException en los routers no deben contener
    palabras sin tilde de la lista ERRORES_CONOCIDOS.
    """
    py_files  = _collect_files(BACKEND_API, [".py"])
    detail_rx = re.compile(r'detail\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)

    errores = []
    for f in py_files:
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            if line.strip().startswith("#"):
                continue
            m = detail_rx.search(line)
            if not m:
                continue
            detail_str = m.group(1)
            for palabra, correcto in ERRORES_CONOCIDOS:
                rx = re.compile(rf"\b{re.escape(palabra)}\b", re.IGNORECASE)
                if rx.search(detail_str):
                    errores.append(
                        f"[{f}:{lineno}] detail contiene «{palabra}» → «{correcto}»\n  {line.strip()}"
                    )

    assert not errores, (
        f"\n{len(errores)} error(es) en HTTPException detail:\n\n" + "\n".join(errores)
    )


# ─────────────────────────────────────────────────────────────────────────────
# A3 – Consistencia de claves entre idiomas en i18n.js
# ─────────────────────────────────────────────────────────────────────────────

def _extract_lang_block_keys(text: str, lang: str) -> set:
    """Extrae el conjunto de claves del bloque 'lang': { … } de TRANSLATIONS."""
    start_rx = re.compile(
        rf"""(?:['"]{re.escape(lang)}['"]\s*|(?<!['"\\w]){re.escape(lang)}\s*):\s*\{{"""
    )
    m = start_rx.search(text)
    if not m:
        return set()
    brace_start = text.index("{", m.start())
    depth, i = 0, brace_start
    while i < len(text):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                break
        i += 1
    block = text[brace_start : i + 1]
    key_rx = re.compile(r"""(?:['"]([\w]+)['"]\s*:|(\b[\w]+\b)\s*:)""")
    keys = set()
    for km in key_rx.finditer(block):
        k = km.group(1) or km.group(2)
        if k:
            keys.add(k)
    return keys


def test_A3_i18n_mismas_claves_en_tres_idiomas():
    """
    i18n.js debe tener exactamente las mismas claves en los tres bloques
    (es, ca, en). Si falta alguna clave en algún idioma, el test falla
    indicando qué claves faltan en qué idioma.
    """
    i18n_path = FRONTEND_JS / "i18n.js"
    if not i18n_path.exists():
        pytest.skip("i18n.js no existe todavía")

    text = i18n_path.read_text(encoding="utf-8")
    keys_es = _extract_lang_block_keys(text, "es")
    keys_ca = _extract_lang_block_keys(text, "ca")
    keys_en = _extract_lang_block_keys(text, "en")

    assert keys_es, "No se encontraron claves en el bloque 'es'"
    assert keys_ca, "No se encontraron claves en el bloque 'ca'"
    assert keys_en, "No se encontraron claves en el bloque 'en'"

    errores = []
    if keys_es != keys_ca:
        solo_es = keys_es - keys_ca
        solo_ca = keys_ca - keys_es
        if solo_es:
            errores.append(f"Claves en 'es' pero NO en 'ca': {sorted(solo_es)}")
        if solo_ca:
            errores.append(f"Claves en 'ca' pero NO en 'es': {sorted(solo_ca)}")
    if keys_es != keys_en:
        solo_es = keys_es - keys_en
        solo_en = keys_en - keys_es
        if solo_es:
            errores.append(f"Claves en 'es' pero NO en 'en': {sorted(solo_es)}")
        if solo_en:
            errores.append(f"Claves en 'en' pero NO en 'es': {sorted(solo_en)}")

    assert not errores, (
        f"\nLos tres idiomas deben tener las mismas claves:\n\n" + "\n".join(errores)
    )
