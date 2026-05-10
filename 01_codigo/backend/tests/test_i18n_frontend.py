"""
Tests de internacionalización — Cambio B (frontend estático)
============================================================
B6 – Estructura de i18n.js: tres bloques con funciones y claves mínimas.
B7 – Atributos data-i18n en index.html, consistencia con TRANSLATIONS['es'].
"""
import re
import pathlib
import pytest

ROOT          = pathlib.Path(__file__).resolve().parents[3]
FRONTEND_JS   = ROOT / "01_codigo" / "frontend" / "static" / "js"
FRONTEND_HTML = ROOT / "01_codigo" / "frontend" / "templates"
I18N_PATH     = FRONTEND_JS / "i18n.js"

MIN_KEYS_PER_LANG = 15

# Claves mínimas que deben existir en los TRES idiomas (spec Cambio B)
REQUIRED_KEYS = {
    "nav_home", "nav_search", "nav_login", "nav_register", "nav_logout",
    "hero_title", "hero_cta_search",
    "search_button", "search_no_results",
    "booking_confirm", "booking_cancel",
    "auth_login", "auth_register", "auth_email", "auth_password",
    "error_required", "error_generic",
    "general_save", "general_cancel", "general_loading",
    "profile_language",
}


def _read_i18n() -> str:
    assert I18N_PATH.exists(), f"i18n.js no encontrado en {I18N_PATH}"
    return I18N_PATH.read_text(encoding="utf-8")


def _extract_keys_for_lang(text: str, lang: str) -> set:
    """Extrae las claves del bloque 'lang': { … } de TRANSLATIONS."""
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


def _get_data_i18n_refs() -> set:
    refs = set()
    rx = re.compile(r'data-i18n=["\']([^"\']+)["\']')
    for hf in FRONTEND_HTML.rglob("*.html"):
        refs.update(rx.findall(hf.read_text(encoding="utf-8")))
    return refs


# ─────────────────────────────────────────────────────────────────────────────
# B6 – Estructura de i18n.js
# ─────────────────────────────────────────────────────────────────────────────

class TestI18nJsStructure:

    def test_B6_file_exists(self):
        """B6 – i18n.js existe"""
        assert I18N_PATH.exists(), "i18n.js no encontrado"

    def test_B6_es_block_has_min_keys(self):
        """B6 – bloque 'es' tiene ≥ MIN_KEYS_PER_LANG claves"""
        keys = _extract_keys_for_lang(_read_i18n(), "es")
        assert len(keys) >= MIN_KEYS_PER_LANG, \
            f"'es' tiene {len(keys)} claves (mínimo {MIN_KEYS_PER_LANG})"

    def test_B6_ca_block_has_min_keys(self):
        """B6 – bloque 'ca' tiene ≥ MIN_KEYS_PER_LANG claves"""
        keys = _extract_keys_for_lang(_read_i18n(), "ca")
        assert len(keys) >= MIN_KEYS_PER_LANG, \
            f"'ca' tiene {len(keys)} claves (mínimo {MIN_KEYS_PER_LANG})"

    def test_B6_en_block_has_min_keys(self):
        """B6 – bloque 'en' tiene ≥ MIN_KEYS_PER_LANG claves"""
        keys = _extract_keys_for_lang(_read_i18n(), "en")
        assert len(keys) >= MIN_KEYS_PER_LANG, \
            f"'en' tiene {len(keys)} claves (mínimo {MIN_KEYS_PER_LANG})"

    def test_B6_required_keys_in_es(self):
        """B6 – Las claves mínimas obligatorias están en el bloque 'es'"""
        keys   = _extract_keys_for_lang(_read_i18n(), "es")
        missing = REQUIRED_KEYS - keys
        assert not missing, f"Claves requeridas ausentes en 'es': {sorted(missing)}"

    def test_B6_required_keys_in_ca(self):
        """B6 – Las claves mínimas obligatorias están en el bloque 'ca'"""
        keys   = _extract_keys_for_lang(_read_i18n(), "ca")
        missing = REQUIRED_KEYS - keys
        assert not missing, f"Claves requeridas ausentes en 'ca': {sorted(missing)}"

    def test_B6_required_keys_in_en(self):
        """B6 – Las claves mínimas obligatorias están en el bloque 'en'"""
        keys   = _extract_keys_for_lang(_read_i18n(), "en")
        missing = REQUIRED_KEYS - keys
        assert not missing, f"Claves requeridas ausentes en 'en': {sorted(missing)}"

    def test_B6_function_getLang(self):
        """B6 – i18n.js define getLang()"""
        assert "function getLang" in _read_i18n()

    def test_B6_function_setLang(self):
        """B6 – i18n.js define setLang()"""
        assert "function setLang" in _read_i18n()

    def test_B6_function_applyTranslations(self):
        """B6 – i18n.js define applyTranslations()"""
        assert "function applyTranslations" in _read_i18n()

    def test_B6_function_t(self):
        """B6 – i18n.js define t()"""
        text = _read_i18n()
        assert "function t(" in text or "function t (" in text


# ─────────────────────────────────────────────────────────────────────────────
# B7 – Atributos data-i18n en el HTML
# ─────────────────────────────────────────────────────────────────────────────

class TestDataI18nHtml:

    def test_B7_html_has_at_least_15_data_i18n(self):
        """B7 – index.html tiene al menos 15 elementos con data-i18n"""
        refs = _get_data_i18n_refs()
        assert len(refs) >= 15, \
            f"Solo {len(refs)} claves data-i18n únicas en el HTML (mínimo 15)"

    def test_B7_all_html_keys_in_es_translations(self):
        """B7 – Cada clave data-i18n del HTML está definida en TRANSLATIONS['es']"""
        es_keys   = _extract_keys_for_lang(_read_i18n(), "es")
        html_refs = _get_data_i18n_refs()
        missing   = html_refs - es_keys
        assert not missing, \
            f"Claves data-i18n sin definición en TRANSLATIONS['es']: {sorted(missing)}"

    def test_B7_i18n_loaded_before_main(self):
        """B7 – i18n.js se carga antes que main.js en el HTML"""
        for hf in FRONTEND_HTML.rglob("*.html"):
            content  = hf.read_text(encoding="utf-8")
            i18n_pos = content.find("i18n.js")
            main_pos = content.find("main.js")
            if i18n_pos != -1 and main_pos != -1:
                assert i18n_pos < main_pos, \
                    f"En {hf}: i18n.js debe cargarse ANTES que main.js"

    def test_B7_lang_selector_present(self):
        """B7 – El HTML contiene botones de selector de idioma (data-lang='es/ca/en')"""
        for hf in FRONTEND_HTML.rglob("*.html"):
            content = hf.read_text(encoding="utf-8")
            if "data-lang" in content:
                assert 'data-lang="es"' in content or "data-lang='es'" in content
                assert 'data-lang="ca"' in content or "data-lang='ca'" in content
                assert 'data-lang="en"' in content or "data-lang='en'" in content
                return
        pytest.fail("No se encontró selector de idioma (data-lang) en el HTML")
