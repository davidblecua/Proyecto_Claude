"""
Tests de internacionalización — Cambio B (frontend estático)
============================================================
B6 – i18n.js existe y contiene los tres idiomas (es, ca, en) con ≥ 15 claves cada uno.
B7 – Todas las claves data-i18n del HTML existen en TRANSLATIONS['es'] de i18n.js.
"""
import re
import pathlib

ROOT          = pathlib.Path(__file__).resolve().parents[3]
FRONTEND_JS   = ROOT / "01_codigo" / "frontend" / "static" / "js"
FRONTEND_HTML = ROOT / "01_codigo" / "frontend" / "templates"
I18N_PATH     = FRONTEND_JS / "i18n.js"

MIN_KEYS_PER_LANG = 15


def _read_i18n():
    assert I18N_PATH.exists(), f"i18n.js no encontrado en {I18N_PATH}"
    return I18N_PATH.read_text(encoding="utf-8")


def _extract_keys_for_lang(text: str, lang: str) -> set:
    """
    Extrae las claves del bloque de un idioma en TRANSLATIONS.
    Soporta claves con o sin comillas: es: { ... }  o  'es': { ... }.
    """
    # Busca 'lang': {  o  "lang": {  o  lang: {
    start_rx = re.compile(
        rf"""(?:['"]{re.escape(lang)}['"]\s*|(?<!['\"\w]){re.escape(lang)}\s*):\s*\{{"""
    )
    m = start_rx.search(text)
    if not m:
        return set()
    # Extraer bloque balanceado
    brace_start = text.index('{', m.start())
    depth = 0
    i = brace_start
    while i < len(text):
        if text[i] == '{':
            depth += 1
        elif text[i] == '}':
            depth -= 1
            if depth == 0:
                break
        i += 1
    block = text[brace_start : i + 1]
    # Extraer claves con o sin comillas:  nav_home:  o  'nav_home':  o  "nav_home":
    key_rx = re.compile(r"""(?:['"]([\w]+)['"]\s*:|(\b[\w]+\b)\s*:)""")
    keys = set()
    for m2 in key_rx.finditer(block):
        k = m2.group(1) or m2.group(2)
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

class TestI18nJsExists:

    def test_B6_i18n_file_exists(self):
        """B6a – i18n.js existe"""
        assert I18N_PATH.exists(), "i18n.js no encontrado"

    def test_B6_has_es_keys(self):
        """B6b – bloque 'es' tiene ≥ MIN_KEYS claves"""
        text = _read_i18n()
        keys = _extract_keys_for_lang(text, 'es')
        assert len(keys) >= MIN_KEYS_PER_LANG, (
            f"'es' tiene solo {len(keys)} claves (mínimo {MIN_KEYS_PER_LANG})"
        )

    def test_B6_has_ca_keys(self):
        """B6c – bloque 'ca' tiene ≥ MIN_KEYS claves"""
        text = _read_i18n()
        keys = _extract_keys_for_lang(text, 'ca')
        assert len(keys) >= MIN_KEYS_PER_LANG, (
            f"'ca' tiene solo {len(keys)} claves (mínimo {MIN_KEYS_PER_LANG})"
        )

    def test_B6_has_en_keys(self):
        """B6d – bloque 'en' tiene ≥ MIN_KEYS claves"""
        text = _read_i18n()
        keys = _extract_keys_for_lang(text, 'en')
        assert len(keys) >= MIN_KEYS_PER_LANG, (
            f"'en' tiene solo {len(keys)} claves (mínimo {MIN_KEYS_PER_LANG})"
        )

    def test_B6_contains_setLang_function(self):
        """B6e – i18n.js define setLang()"""
        text = _read_i18n()
        assert 'function setLang' in text, "setLang no definida en i18n.js"

    def test_B6_contains_getLang_function(self):
        """B6f – i18n.js define getLang()"""
        text = _read_i18n()
        assert 'function getLang' in text, "getLang no definida en i18n.js"

    def test_B6_contains_t_function(self):
        """B6g – i18n.js define t()"""
        text = _read_i18n()
        assert 'function t(' in text or 'function t (' in text, "t() no definida en i18n.js"

    def test_B6_contains_applyTranslations(self):
        """B6h – i18n.js define applyTranslations()"""
        text = _read_i18n()
        assert 'function applyTranslations' in text, "applyTranslations no definida en i18n.js"


class TestDataI18nConsistency:

    def test_B7_html_has_data_i18n_attributes(self):
        """B7a – El HTML tiene al menos 15 atributos data-i18n"""
        refs = _get_data_i18n_refs()
        assert len(refs) >= 15, (
            f"Solo {len(refs)} claves data-i18n únicas en el HTML (mínimo 15)"
        )

    def test_B7_all_html_keys_in_es_translations(self):
        """B7b – Cada clave data-i18n del HTML está definida en TRANSLATIONS['es']"""
        text    = _read_i18n()
        es_keys = _extract_keys_for_lang(text, 'es')
        html_refs = _get_data_i18n_refs()

        missing = html_refs - es_keys
        assert not missing, (
            f"Claves data-i18n sin definición en TRANSLATIONS['es']: {sorted(missing)}"
        )

    def test_B7_i18n_loaded_before_main(self):
        """B7c – i18n.js se carga antes que main.js en el HTML"""
        for hf in FRONTEND_HTML.rglob("*.html"):
            content = hf.read_text(encoding="utf-8")
            i18n_pos = content.find('i18n.js')
            main_pos = content.find('main.js')
            if i18n_pos != -1 and main_pos != -1:
                assert i18n_pos < main_pos, (
                    f"En {hf}: i18n.js debe cargarse ANTES que main.js"
                )

    def test_B7_lang_selector_in_html(self):
        """B7d – El HTML contiene los botones del selector de idioma"""
        for hf in FRONTEND_HTML.rglob("*.html"):
            content = hf.read_text(encoding="utf-8")
            if 'data-lang' in content:
                assert "data-lang=\"es\"" in content or "data-lang='es'" in content
                assert "data-lang=\"ca\"" in content or "data-lang='ca'" in content
                assert "data-lang=\"en\"" in content or "data-lang='en'" in content
                return
        pytest.fail("No se encontró selector de idioma con data-lang en el HTML")
