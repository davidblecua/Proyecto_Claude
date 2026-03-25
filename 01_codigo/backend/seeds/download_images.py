"""
Descarga fotos reales de Wikimedia Commons para cada tipo de maquinaria
y actualiza la base de datos con las rutas locales.
"""
import sys
import os
import json
import urllib.request
import urllib.error

# Agrega la ruta del backend al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal
from app.models.user import User  # noqa: F401 – necesario para que SQLAlchemy resuelva la relación
from app.models.machinery import Machinery, MachineryType
from app.models.booking import Booking  # noqa: F401

STATIC_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    '..', 'frontend', 'static', 'images', 'machinery'
)

# Un representante visual por cada tipo de maquinaria (Wikimedia Commons, licencia libre)
TYPE_IMAGES = {
    MachineryType.EXCAVADORA: {
        "url": "https://upload.wikimedia.org/wikipedia/commons/a/a2/Caterpillar_320.jpg",
        "filename": "caterpillar_320.jpg",
    },
    MachineryType.RETROEXCAVADORA: {
        "url": "https://upload.wikimedia.org/wikipedia/commons/f/f5/JCB_3CX_backhoe_loader.JPG",
        "filename": "jcb_3cx.jpg",
    },
    MachineryType.BULLDOZER: {
        "url": "https://upload.wikimedia.org/wikipedia/commons/b/b1/Caterpillar_D6_bulldozer_VA2.jpg",
        "filename": "caterpillar_d6.jpg",
    },
    MachineryType.PALA_CARGADORA: {
        "url": "https://upload.wikimedia.org/wikipedia/commons/6/69/CATERPILLAR_950_GC_Wheel_Loader_02.jpg",
        "filename": "caterpillar_950.jpg",
    },
    MachineryType.DUMPER: {
        "url": "https://upload.wikimedia.org/wikipedia/commons/3/31/AUSA_dumper_2.jpg",
        "filename": "ausa_dumper.jpg",
    },
    MachineryType.HORMIGONERA: {
        "url": "https://upload.wikimedia.org/wikipedia/commons/5/51/Small-transit-mixer.jpg",
        "filename": "hormigonera.jpg",
    },
    MachineryType.CAMION_GRUA: {
        "url": "https://upload.wikimedia.org/wikipedia/commons/d/dd/Hiab_Autokrananzeige.jpg",
        "filename": "hiab_camion_grua.jpg",
    },
    MachineryType.GRUA_TORRE: {
        "url": "https://upload.wikimedia.org/wikipedia/commons/3/30/Potain_tower_crane%2C_France.jpg",
        "filename": "potain_grua_torre.jpg",
    },
    MachineryType.MANIPULADOR_TELESCOPICO: {
        "url": "https://upload.wikimedia.org/wikipedia/commons/b/b5/MERLO_Panoramic_Telescopic_handler_pic3.JPG",
        "filename": "merlo_telescopico.jpg",
    },
    MachineryType.PLATAFORMA_ELEVADORA: {
        "url": "https://upload.wikimedia.org/wikipedia/commons/e/ed/Articulated_boom_lift_%2820240319%29.jpg",
        "filename": "plataforma_elevadora.jpg",
    },
    MachineryType.CARRETILLA_ELEVADORA: {
        "url": "https://upload.wikimedia.org/wikipedia/commons/b/bc/Carretilla_nisan_2.500kg.jpg",
        "filename": "carretilla_elevadora.jpg",
    },
    MachineryType.COMPACTADORA: {
        "url": "https://upload.wikimedia.org/wikipedia/commons/4/4f/Bomag_road_rollers_23.jpg",
        "filename": "bomag_compactadora.jpg",
    },
    MachineryType.MOTONIVELADORA: {
        "url": "https://upload.wikimedia.org/wikipedia/commons/d/da/Caterpillar_motor_grader_engine_AGSEM.jpg",
        "filename": "caterpillar_motoniveladora.jpg",
    },
    MachineryType.MARTILLO_HIDRAULICO: {
        "url": "https://upload.wikimedia.org/wikipedia/commons/b/b9/Hydraulikbreaker_LST_XB5100is_2009-01.jpg",
        "filename": "martillo_hidraulico.jpg",
    },
    MachineryType.COMPRESOR: {
        "url": "https://upload.wikimedia.org/wikipedia/commons/0/04/Atlas_Copco_XAHS_347-pic3.jpg",
        "filename": "atlas_copco_compresor.jpg",
    },
    MachineryType.GENERADOR: {
        "url": "https://upload.wikimedia.org/wikipedia/commons/7/73/Worcestershire_Royal_Hospital_-_portable_diesel_generator_-_geograph.org.uk_-_6884678.jpg",
        "filename": "generador_diesel.jpg",
    },
    MachineryType.MONTACARGAS: {
        "url": "https://upload.wikimedia.org/wikipedia/commons/c/c0/Lift-climber-mast.jpg",
        "filename": "montacargas_obra.jpg",
    },
    MachineryType.BOMBA_HORMIGON: {
        "url": "https://upload.wikimedia.org/wikipedia/commons/e/ef/Putzmeister_concrete_pump.JPEG",
        "filename": "putzmeister_bomba.jpg",
    },
    MachineryType.CORTADORA_ASFALTO: {
        "url": "https://upload.wikimedia.org/wikipedia/commons/a/ac/I_Need_a_Bigger_Saw...._DVIDS110119.jpg",
        "filename": "cortadora_asfalto.jpg",
    },
    MachineryType.ANDAMIO: {
        "url": "https://upload.wikimedia.org/wikipedia/commons/3/3b/Wiederaufbau_Teepavillon_WBW_modular_system_scaffold.jpg",
        "filename": "andamio_sistema.jpg",
    },
}


def download_image(url: str, dest_path: str) -> bool:
    """Descarga una imagen de Wikimedia Commons."""
    if os.path.exists(dest_path):
        print(f"  [SKIP] Ya existe: {os.path.basename(dest_path)}")
        return True
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "RentaMaqBot/1.0 (educational project)"})
        with urllib.request.urlopen(req, timeout=30) as response:
            data = response.read()
        with open(dest_path, 'wb') as f:
            f.write(data)
        size_kb = len(data) // 1024
        print(f"  [OK] {os.path.basename(dest_path)} ({size_kb} KB)")
        return True
    except urllib.error.HTTPError as e:
        print(f"  [ERROR HTTP {e.code}] {url}")
        return False
    except Exception as e:
        print(f"  [ERROR] {url}: {e}")
        return False


def update_db(db, machinery_type: MachineryType, web_path: str):
    """Actualiza el campo images de todas las máquinas de ese tipo."""
    machines = db.query(Machinery).filter(
        Machinery.machinery_type == machinery_type,
        Machinery.is_active == True
    ).all()
    for m in machines:
        m.images = json.dumps([web_path])
    db.commit()
    return len(machines)


def main():
    db = SessionLocal()
    try:
        total_downloaded = 0
        total_updated = 0

        for mtype, info in TYPE_IMAGES.items():
            type_name = mtype.value
            print(f"\n{'='*50}")
            print(f"Tipo: {type_name}")

            # Ruta local para guardar la imagen
            folder = os.path.join(STATIC_DIR, type_name)
            os.makedirs(folder, exist_ok=True)
            dest_path = os.path.join(folder, info["filename"])

            # Descargar imagen
            ok = download_image(info["url"], dest_path)
            if ok:
                total_downloaded += 1

            # Ruta web que usará el frontend
            web_path = f"/static/images/machinery/{type_name}/{info['filename']}"

            # Actualizar BD
            updated = update_db(db, mtype, web_path)
            total_updated += updated
            print(f"  [BD] {updated} máquinas actualizadas con: {web_path}")

        print(f"\n{'='*50}")
        print(f"Resumen: {total_downloaded}/20 imágenes descargadas, {total_updated} registros actualizados")

    finally:
        db.close()


if __name__ == "__main__":
    main()
