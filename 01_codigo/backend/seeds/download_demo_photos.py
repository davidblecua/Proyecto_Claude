#!/usr/bin/env python3
"""
Descarga fotos reales de Wikimedia Commons para la demo de RentaMaq.
Ejecutar UNA VEZ antes de seed_demo.py (tarda ~2 minutos por el rate-limit).

Uso:  python seeds/download_demo_photos.py
      Ejecutar desde: 01_codigo/backend/
"""
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

FRONTEND_STATIC = Path(__file__).resolve().parent.parent.parent / "frontend" / "static"

# Fotos de Wikimedia Commons (licencia libre) — una por tipo de maquinaria
PHOTOS = [
    ("excavadora",             "exc_1.jpg",   "https://upload.wikimedia.org/wikipedia/commons/a/a2/Caterpillar_320.jpg"),
    ("retroexcavadora",        "ret_1.jpg",   "https://upload.wikimedia.org/wikipedia/commons/f/f5/JCB_3CX_backhoe_loader.JPG"),
    ("plataforma_elevadora",   "plat_1.jpg",  "https://upload.wikimedia.org/wikipedia/commons/e/ed/Articulated_boom_lift_%2820240319%29.jpg"),
    ("grua_torre",             "grua_1.jpg",  "https://upload.wikimedia.org/wikipedia/commons/3/30/Potain_tower_crane%2C_France.jpg"),
    ("dumper",                 "dump_1.jpg",  "https://upload.wikimedia.org/wikipedia/commons/3/31/AUSA_dumper_2.jpg"),
    ("manipulador_telescopico","mani_1.jpg",  "https://upload.wikimedia.org/wikipedia/commons/b/b5/MERLO_Panoramic_Telescopic_handler_pic3.JPG"),
    ("compactadora",           "comp_1.jpg",  "https://upload.wikimedia.org/wikipedia/commons/4/4f/Bomag_road_rollers_23.jpg"),
    ("pala_cargadora",         "pala_1.jpg",  "https://upload.wikimedia.org/wikipedia/commons/6/69/CATERPILLAR_950_GC_Wheel_Loader_02.jpg"),
    ("bomba_hormigon",         "bomb_1.jpg",  "https://upload.wikimedia.org/wikipedia/commons/e/ef/Putzmeister_concrete_pump.JPEG"),
    ("carretilla_elevadora",   "carr_1.jpg",  "https://upload.wikimedia.org/wikipedia/commons/b/bc/Carretilla_nisan_2.500kg.jpg"),
]

DELAY_BETWEEN = 12   # segundos entre descargas (límite Wikimedia: ~1 req/10 s)
TIMEOUT       = 45   # segundos de timeout por request


def download(url: str, dest: Path) -> bool:
    """Descarga url a dest. Devuelve True si ok."""
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "RentaMaqBot/1.0 (educational project; davidblecua98@gmail.com)"}
        )
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            data = r.read()
        dest.write_bytes(data)
        print(f"  ✓ {dest.name}  ({len(data) // 1024} KB)")
        return True
    except urllib.error.HTTPError as e:
        print(f"  ✗ HTTP {e.code} — {dest.name}")
        return False
    except Exception as e:
        print(f"  ✗ {dest.name}: {e}")
        return False


def main():
    print("Descargando fotos de maquinaria (Wikimedia Commons)…")
    print(f"Delay entre descargas: {DELAY_BETWEEN} s\n")

    ok = skip = fail = 0
    for i, (mtype, fname, url) in enumerate(PHOTOS):
        folder = FRONTEND_STATIC / "images" / "machinery" / mtype
        folder.mkdir(parents=True, exist_ok=True)
        dest = folder / fname

        if dest.exists():
            print(f"  ↷ {fname}  (ya existe)")
            skip += 1
            continue

        if i > 0:
            remaining = len(PHOTOS) - i
            print(f"  ⏳ esperando {DELAY_BETWEEN} s…  (quedan {remaining} fotos)")
            time.sleep(DELAY_BETWEEN)

        print(f"[{i+1}/{len(PHOTOS)}] {mtype}")
        if download(url, dest):
            ok += 1
        else:
            fail += 1

    print(f"\nResultado: {ok} descargadas · {skip} ya existían · {fail} fallidas")
    if fail:
        print("Repite el script para reintentar las fallidas (son idempotente).")
    else:
        print("Listo. Ejecuta ahora: python seeds/seed_demo.py --env dev")

    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
