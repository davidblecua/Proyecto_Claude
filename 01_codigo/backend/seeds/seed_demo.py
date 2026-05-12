#!/usr/bin/env python3
"""
Seed de demo para RentaMaq.
Uso:  python seeds/seed_demo.py --env dev
      python seeds/seed_demo.py --env pre
Ejecutar desde: 01_codigo/backend/

Credenciales demo fijas:
  Propietario : david@demo.com    / Demo1234!
  Cliente     : cliente@demo.com  / Demo1234!
  Admin       : admin@demo.com    / Demo1234!
"""
import sys
import os
import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# Directorio static del frontend (para guardar las fotos descargadas)
_FRONTEND_STATIC = Path(__file__).resolve().parent.parent.parent / "frontend" / "static"

# ── Fotos reales de Wikimedia Commons por tipo de maquinaria ─────────────────
# Licencia libre; se descargan localmente al ejecutar el seed.
WIKIMEDIA_PHOTOS: dict[str, list[tuple[str, str]]] = {
    "excavadora": [
        ("https://upload.wikimedia.org/wikipedia/commons/a/a2/Caterpillar_320.jpg",          "exc_1.jpg"),
    ],
    "retroexcavadora": [
        ("https://upload.wikimedia.org/wikipedia/commons/f/f5/JCB_3CX_backhoe_loader.JPG",  "ret_1.jpg"),
    ],
    "plataforma_elevadora": [
        ("https://upload.wikimedia.org/wikipedia/commons/e/ed/Articulated_boom_lift_%2820240319%29.jpg", "plat_1.jpg"),
    ],
    "grua_torre": [
        ("https://upload.wikimedia.org/wikipedia/commons/3/30/Potain_tower_crane%2C_France.jpg", "grua_1.jpg"),
    ],
    "dumper": [
        ("https://upload.wikimedia.org/wikipedia/commons/3/31/AUSA_dumper_2.jpg",            "dump_1.jpg"),
    ],
    "manipulador_telescopico": [
        ("https://upload.wikimedia.org/wikipedia/commons/b/b5/MERLO_Panoramic_Telescopic_handler_pic3.JPG", "mani_1.jpg"),
    ],
    "compactadora": [
        ("https://upload.wikimedia.org/wikipedia/commons/4/4f/Bomag_road_rollers_23.jpg",    "comp_1.jpg"),
    ],
    "pala_cargadora": [
        ("https://upload.wikimedia.org/wikipedia/commons/6/69/CATERPILLAR_950_GC_Wheel_Loader_02.jpg", "pala_1.jpg"),
    ],
    "bomba_hormigon": [
        ("https://upload.wikimedia.org/wikipedia/commons/e/ef/Putzmeister_concrete_pump.JPEG", "bomb_1.jpg"),
    ],
    "carretilla_elevadora": [
        ("https://upload.wikimedia.org/wikipedia/commons/b/bc/Carretilla_nisan_2.500kg.jpg", "carr_1.jpg"),
    ],
}


def fetch_type_photos(mtype_str: str) -> list[str]:
    """Devuelve las rutas web locales de las fotos de un tipo de maquinaria.

    Las fotos deben haber sido descargadas previamente con download_demo_photos.py.
    Si el archivo no existe localmente, lo omite.
    """
    sources = WIKIMEDIA_PHOTOS.get(mtype_str, [])
    result: list[str] = []
    for _url, fname in sources:
        dest = _FRONTEND_STATIC / "images" / "machinery" / mtype_str / fname
        if dest.exists():
            result.append(f"/static/images/machinery/{mtype_str}/{fname}")
    return result


def load_env(env: str):
    env_file = Path(__file__).parent.parent / f".env.{env}"
    if not env_file.exists():
        print(f"Error: {env_file} no encontrado")
        sys.exit(1)
    from dotenv import load_dotenv
    load_dotenv(env_file, override=True)
    os.environ["APP_ENV"] = env
    print(f"Entorno cargado: {env_file.name}")


def get_engine_and_session():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    user = os.environ["DATABASE_USER"]
    pwd  = os.environ["DATABASE_PASSWORD"]
    host = os.environ["DATABASE_HOST"]
    port = os.environ.get("DATABASE_PORT", "5432")
    name = os.environ["DATABASE_NAME"]
    url  = f"postgresql://{user}:{pwd}@{host}:{port}/{name}"
    engine = create_engine(url, pool_pre_ping=True)
    return engine, sessionmaker(bind=engine)()


def hash_password(password: str) -> str:
    from passlib.context import CryptContext
    return CryptContext(schemes=["bcrypt"], deprecated="auto").hash(password)


def main():
    parser = argparse.ArgumentParser(description="Seed de demo para RentaMaq")
    parser.add_argument("--env", required=True, choices=["dev", "pre", "pro"],
                        help="Entorno objetivo (dev | pre | pro)")
    args = parser.parse_args()

    load_env(args.env)
    engine, db = get_engine_and_session()

    from app.db.database import Base
    from app.models.user import User, UserRole
    from app.models.machinery import Machinery, MachineryType, MachineryCondition
    from app.models.operator import Operator
    from app.models.booking import Booking, BookingStatus
    from app.models.review import Review, TargetType
    from app.models.machinery_request import MachineryRequest, RequestStatus
    from app.models.message import Message

    Base.metadata.create_all(bind=engine)

    now = datetime.now(timezone.utc)

    # ── 1. USUARIOS ───────────────────────────────────────────────────────────
    print("\n[1/7] Usuarios...")
    users_data = [
        # ── Credenciales demo fijas (para presentación) ──
        {"email": "david@demo.com",     "username": "david_demo",     "full_name": "David (Demo)",          "role": UserRole.PUBLISHER, "pwd": "Demo1234!", "company": "Maquinaria Demo SL",   "address": "Lleida"},
        {"email": "cliente@demo.com",   "username": "cliente_demo",   "full_name": "Cliente Demo",          "role": UserRole.CONSUMER,  "pwd": "Demo1234!"},
        {"email": "admin@demo.com",     "username": "admin_demo",     "full_name": "Admin Demo",            "role": UserRole.ADMIN,     "pwd": "Demo1234!", "company": "RentaMaq SL"},
        # ── Usuarios de relleno ──
        {"email": "admin@rentamaq.com",          "username": "admin_rentamaq",     "full_name": "Administrador Principal", "role": UserRole.ADMIN,     "pwd": "Admin1234",  "company": "RentaMaq SL"},
        {"email": "maquinaria@olivasl.com",      "username": "maquinaria_oliva",   "full_name": "Maquinaria Oliva SL",    "role": UserRole.PUBLISHER, "pwd": "Test1234",   "company": "Maquinaria Oliva SL",   "address": "Barcelona"},
        {"email": "info@gruasmedina.com",         "username": "gruas_medina",       "full_name": "Grúas Medina SA",        "role": UserRole.PUBLISHER, "pwd": "Test1234",   "company": "Grúas Medina SA",       "address": "Madrid"},
        {"email": "contacto@equiposfontana.com", "username": "equipos_fontana",    "full_name": "Equipos Fontana",        "role": UserRole.PUBLISHER, "pwd": "Test1234",   "company": "Equipos Fontana SL",    "address": "Valencia"},
        {"email": "roca@construccionesroca.es",  "username": "construcciones_roca","full_name": "Construcciones Roca",    "role": UserRole.PUBLISHER, "pwd": "Test1234",   "company": "Construcciones Roca SL","address": "Sevilla"},
        {"email": "carlos.perez@obrasnorte.com",         "username": "carlos_perez",   "full_name": "Carlos Pérez García",  "role": UserRole.CONSUMER, "pwd": "Test1234"},
        {"email": "m.gonzalez@constructoraoliva.com",    "username": "maria_gonzalez", "full_name": "María González López", "role": UserRole.CONSUMER, "pwd": "Test1234"},
        {"email": "j.ruiz@grupofontana.com",             "username": "javier_ruiz",    "full_name": "Javier Ruiz Martínez", "role": UserRole.CONSUMER, "pwd": "Test1234"},
        {"email": "a.martinez@edificacionesroca.es",     "username": "ana_martinez",   "full_name": "Ana Martínez Sánchez", "role": UserRole.CONSUMER, "pwd": "Test1234"},
    ]

    users = {}
    for u in users_data:
        existing = db.query(User).filter(User.email == u["email"]).first()
        if existing:
            print(f"  ↳ {u['email']}")
            users[u["email"]] = existing
            continue
        obj = User(
            email=u["email"], username=u["username"], full_name=u.get("full_name"),
            hashed_password=hash_password(u["pwd"]), role=u["role"],
            is_active=True, is_verified=True,
            company_name=u.get("company"), address=u.get("address"),
            preferred_language="es",
        )
        db.add(obj)
        db.flush()
        users[u["email"]] = obj
        print(f"  ✓ {u['email']}")
    db.commit()

    david   = users["david@demo.com"]
    cliente = users["cliente@demo.com"]
    oliva   = users["maquinaria@olivasl.com"]
    medina  = users["info@gruasmedina.com"]
    fontana = users["contacto@equiposfontana.com"]
    roca    = users["roca@construccionesroca.es"]
    carlos  = users["carlos.perez@obrasnorte.com"]
    maria   = users["m.gonzalez@constructoraoliva.com"]
    javier  = users["j.ruiz@grupofontana.com"]
    ana     = users["a.martinez@edificacionesroca.es"]

    # ── 2. MAQUINARIA (con fotos reales de Wikimedia) ────────────────────────
    print("\n[2/7] Maquinaria...")
    machinery_data = [
        # david@demo.com — Lleida (máquinas destacadas para la demo)
        {"title": "Excavadora CAT 320 GC – Demo",   "owner": david,   "type": MachineryType.EXCAVADORA,            "brand": "Caterpillar", "model": "320 GC",     "year": 2022, "rate": 420, "city": "Lleida",       "province": "Lleida",     "condition": MachineryCondition.EXCELENTE, "req_op": True,  "delivery": True,  "del_cost": 150, "deposit": 2000, "desc": "Excavadora de cadenas 20 t, cazo 1,2 m³. GPS integrado, mantenimiento al día. Lista para obra de inmediato."},
        {"title": "Retroexcavadora JCB 3CX – Demo", "owner": david,   "type": MachineryType.RETROEXCAVADORA,       "brand": "JCB",         "model": "3CX",        "year": 2021, "rate": 300, "city": "Lleida",       "province": "Lleida",     "condition": MachineryCondition.EXCELENTE, "req_lic": True, "delivery": True,  "del_cost": 100, "deposit": 1500, "desc": "Retroexcavadora combinada 4×4. Profundidad 5,6 m, cazo 30 cm incluido. Ideal para zanjas y cimentaciones."},
        {"title": "Dumper Wacker 3001 – Demo",       "owner": david,   "type": MachineryType.DUMPER,                "brand": "Wacker Neuson","model": "3001",       "year": 2020, "rate": 180, "city": "Lleida",       "province": "Lleida",     "condition": MachineryCondition.BUENO,     "deposit": 800,  "desc": "Dumper articulado carga frontal 3.000 kg. Perfecto para obras en pendiente y espacios reducidos."},
        # Oliva SL — Barcelona
        {"title": "Excavadora Caterpillar 320 GC",   "owner": oliva,   "type": MachineryType.EXCAVADORA,            "brand": "Caterpillar", "model": "320 GC",     "year": 2021, "rate": 450, "city": "Barcelona",    "province": "Barcelona",  "condition": MachineryCondition.EXCELENTE, "req_op": True,  "delivery": True,  "del_cost": 180, "deposit": 2000, "desc": "Excavadora de cadenas de 20 toneladas, cazo 1,2 m³. Mantenimiento al día, lista para obra."},
        {"title": "Retroexcavadora JCB 3CX",         "owner": oliva,   "type": MachineryType.RETROEXCAVADORA,       "brand": "JCB",         "model": "3CX",        "year": 2020, "rate": 320, "city": "Badalona",     "province": "Barcelona",  "condition": MachineryCondition.BUENO,     "req_lic": True, "delivery": True,  "del_cost": 120, "deposit": 1500, "desc": "Retroexcavadora combinada 4x4. Profundidad 5,6 m, cazo de 30 cm incluido."},
        {"title": "Plataforma Elevadora Dingli AWSP200S", "owner": oliva, "type": MachineryType.PLATAFORMA_ELEVADORA, "brand": "Dingli",  "model": "AWSP200S",   "year": 2022, "rate": 280, "city": "Sabadell",     "province": "Barcelona",  "condition": MachineryCondition.EXCELENTE, "delivery": True,  "del_cost": 150, "deposit": 1200, "desc": "Plataforma articulada autopropulsada 20 m, tracción 4x4. Carné IPAF requerido."},
        # Grúas Medina — Madrid
        {"title": "Grúa Torre Liebherr 63K",         "owner": medina,  "type": MachineryType.GRUA_TORRE,            "brand": "Liebherr",    "model": "63K",        "year": 2019, "rate": 580, "city": "Madrid",       "province": "Madrid",     "condition": MachineryCondition.BUENO,     "req_op": True,  "insur": True,    "deposit": 3000, "desc": "Grúa torre de montaje rápido, pluma 45 m, cap. 6 t. Incluye montaje y desmontaje."},
        {"title": "Dumper Wacker Neuson 3001",        "owner": medina,  "type": MachineryType.DUMPER,                "brand": "Wacker Neuson","model": "3001",       "year": 2020, "rate": 190, "city": "Alcalá de Henares","province": "Madrid", "condition": MachineryCondition.BUENO,     "deposit": 800,  "desc": "Dumper articulado carga frontal 3.000 kg. Ideal para pendientes pronunciadas."},
        {"title": "Manipulador Telescópico Merlo P40.17","owner": medina,"type": MachineryType.MANIPULADOR_TELESCOPICO,"brand": "Merlo",    "model": "P40.17",     "year": 2021, "rate": 380, "city": "Getafe",       "province": "Madrid",     "condition": MachineryCondition.EXCELENTE, "req_lic": True, "delivery": True,  "del_cost": 200, "deposit": 2000, "desc": "4 t y 17 m de alcance. Horquillas, cazo y pluma incluidos."},
        # Equipos Fontana — Valencia
        {"title": "Compactadora Hamm HD 12 VV",      "owner": fontana, "type": MachineryType.COMPACTADORA,          "brand": "Hamm",        "model": "HD 12 VV",   "year": 2020, "rate": 210, "city": "Valencia",     "province": "Valencia",   "condition": MachineryCondition.BUENO,     "delivery": True,  "del_cost": 100, "deposit": 900,  "desc": "Compactadora vibratoria doble rodillo 1.200 kg. Ideal asfalto en capas delgadas."},
        {"title": "Minicargadora Bobcat S450",        "owner": fontana, "type": MachineryType.PALA_CARGADORA,       "brand": "Bobcat",      "model": "S450",       "year": 2021, "rate": 240, "city": "Torrent",      "province": "Valencia",   "condition": MachineryCondition.EXCELENTE, "deposit": 1100, "desc": "680 kg de capacidad. Perfecta para interiores y espacios confinados."},
        {"title": "Bomba de Hormigón Putzmeister BSA 1407 D","owner": fontana,"type": MachineryType.BOMBA_HORMIGON,"brand": "Putzmeister","model": "BSA 1407 D","year": 2018,  "rate": 490, "city": "Alicante",     "province": "Alicante",   "condition": MachineryCondition.ACEPTABLE, "req_op": True,  "deposit": 2500, "desc": "Caudal 70 m³/h, presión 140 bar. Mangueras 30 m incluidas."},
        # Construcciones Roca — Sevilla
        {"title": "Carretilla Elevadora Toyota 8FBN25","owner": roca,   "type": MachineryType.CARRETILLA_ELEVADORA,  "brand": "Toyota",     "model": "8FBN25",     "year": 2022, "rate": 155, "city": "Sevilla",      "province": "Sevilla",    "condition": MachineryCondition.EXCELENTE, "req_lic": True, "deposit": 700,  "desc": "Eléctrica 2.500 kg, altura 5,5 m. Cero emisiones, ideal naves industriales."},
        {"title": "Excavadora Komatsu PC210LC",       "owner": roca,    "type": MachineryType.EXCAVADORA,            "brand": "Komatsu",    "model": "PC210LC",    "year": 2020, "rate": 470, "city": "Dos Hermanas", "province": "Sevilla",    "condition": MachineryCondition.BUENO,     "req_op": True,  "delivery": True,  "del_cost": 220, "deposit": 2200, "desc": "21 toneladas, motor Stage V, GPS de posicionamiento incluido."},
        {"title": "Retroexcavadora Case 580N",        "owner": roca,    "type": MachineryType.RETROEXCAVADORA,       "brand": "Case",       "model": "580N",       "year": 2019, "rate": 340, "city": "Utrera",       "province": "Sevilla",    "condition": MachineryCondition.BUENO,     "delivery": True,  "del_cost": 160, "deposit": 1600, "desc": "4x4, profundidad 5,6 m. Disponible con cuchara bivalva para pozos."},
    ]

    machineries = []
    for m in machinery_data:
        existing = db.query(Machinery).filter(
            Machinery.title == m["title"], Machinery.owner_id == m["owner"].id
        ).first()
        if existing:
            # Actualizar fotos si aún no tiene (o si son URLs externas de Picsum)
            imgs = json.loads(existing.images) if existing.images and existing.images not in ("null", "[]") else []
            needs_update = not imgs or all("picsum" in u for u in imgs)
            if needs_update:
                photos = fetch_type_photos(m["type"].value)
                if photos:
                    existing.images = json.dumps(photos)
                    print(f"  ↳ {m['title']} (fotos actualizadas)")
                else:
                    print(f"  ↳ {m['title']}")
            else:
                print(f"  ↳ {m['title']}")
            machineries.append(existing)
            continue
        photos = fetch_type_photos(m["type"].value)
        obj = Machinery(
            title=m["title"], description=m["desc"],
            machinery_type=m["type"], owner_id=m["owner"].id,
            brand=m.get("brand"), model=m.get("model"), year=m.get("year"),
            condition=m.get("condition", MachineryCondition.BUENO),
            daily_rate=float(m["rate"]),
            weekly_rate=float(m["rate"]) * 5.5,
            monthly_rate=float(m["rate"]) * 20,
            deposit=float(m.get("deposit", 0)),
            location_city=m["city"], location_province=m["province"],
            images=json.dumps(photos),
            is_available=True, is_active=True,
            requires_operator=m.get("req_op", False),
            requires_license=m.get("req_lic", False),
            insurance_included=m.get("insur", False),
            delivery_available=m.get("delivery", False),
            delivery_cost=float(m["del_cost"]) if m.get("del_cost") else None,
        )
        db.add(obj)
        db.flush()
        machineries.append(obj)
        print(f"  ✓ {m['title']}")
    db.commit()

    # Referencias cómodas
    m_david_excav  = machineries[0]   # Excavadora CAT – Demo (david)
    m_david_retro  = machineries[1]   # Retroexcavadora – Demo (david)
    m_david_dumper = machineries[2]   # Dumper – Demo (david)
    m_excav_oliva  = machineries[3]
    m_retro_oliva  = machineries[4]
    m_grua_medina  = machineries[6]
    m_dumper_med   = machineries[7]
    m_compact      = machineries[9]
    m_mini         = machineries[10]
    m_carretilla   = machineries[12]
    m_excav_roca   = machineries[13]

    # ── 3. OPERARIOS ──────────────────────────────────────────────────────────
    print("\n[3/7] Operarios...")
    operators_data = [
        # david@demo.com — operarios propios
        {"name": "Marc Blecua Solsona",      "owner": david,   "skills": ["excavadora", "retroexcavadora"],                    "exp": 12, "rate": 240, "city": "Lleida",           "province": "Lleida",    "desc": "Operador titular de maquinaria pesada con 12 años de experiencia en obra civil y urbanización. Certificado CAP."},
        {"name": "Neus Farré Giménez",       "owner": david,   "skills": ["dumper", "compactadora"],                           "exp": 7,  "rate": 190, "city": "Lleida",           "province": "Lleida",    "desc": "Especialista en movimiento de tierras y trabajos de explanación. Carné C1."},
        # Oliva SL
        {"name": "Tomàs Coll Ferrer",        "owner": oliva,   "skills": ["excavadora", "retroexcavadora"],                    "exp": 14, "rate": 260, "city": "Barcelona",        "province": "Barcelona", "desc": "Operador de excavadoras con 14 años en obra civil. Certificado C1 de maquinaria pesada."},
        {"name": "Rosa Puig Mas",            "owner": oliva,   "skills": ["plataforma_elevadora", "manipulador_telescopico"],  "exp": 9,  "rate": 220, "city": "Sabadell",         "province": "Barcelona", "desc": "Especialista en plataformas elevadoras y trabajos en altura. Carné IPAF."},
        # Grúas Medina
        {"name": "Fernando Medina Ruiz",     "owner": medina,  "skills": ["grua_torre", "camion_grua"],                        "exp": 18, "rate": 380, "city": "Madrid",           "province": "Madrid",    "desc": "Gruista titulado con 18 años. Especialista en montajes de alta complejidad."},
        {"name": "Lucía Serrano Blanco",     "owner": medina,  "skills": ["manipulador_telescopico", "dumper"],                "exp": 7,  "rate": 210, "city": "Alcalá de Henares","province": "Madrid",    "desc": "Operaria de manipuladores telescópicos en edificación residencial y comercial."},
        # Equipos Fontana
        {"name": "Miquel Bosch Ribas",       "owner": fontana, "skills": ["compactadora", "dumper"],                           "exp": 11, "rate": 195, "city": "Valencia",         "province": "Valencia",  "desc": "Especialista en compactación para obra civil. Autopistas y urbanizaciones."},
        {"name": "Carmen Vidal Navarro",     "owner": fontana, "skills": ["bomba_hormigon", "hormigonera"],                    "exp": 13, "rate": 310, "city": "Alicante",         "province": "Alicante",  "desc": "Operaria certificada por Putzmeister. Losas, pilares y soleras."},
        # Construcciones Roca
        {"name": "Antonio Roca Jiménez",     "owner": roca,    "skills": ["excavadora", "bulldozer"],                          "exp": 16, "rate": 285, "city": "Sevilla",          "province": "Sevilla",   "desc": "16 años en movimiento de tierras. Experto en excavación en roca y demolición."},
        {"name": "Isabel Moreno Domínguez",  "owner": roca,    "skills": ["carretilla_elevadora", "manipulador_telescopico"],  "exp": 8,  "rate": 180, "city": "Dos Hermanas",     "province": "Sevilla",   "desc": "Carretillera certificada con amplia experiencia en almacenes y logística de obra."},
    ]

    for o in operators_data:
        if db.query(Operator).filter(Operator.name == o["name"]).first():
            print(f"  ↳ {o['name']}")
            continue
        db.add(Operator(
            owner_id=o["owner"].id, name=o["name"], description=o["desc"],
            daily_rate=float(o["rate"]), experience_years=o["exp"],
            machine_skills=json.dumps(o["skills"]),
            location_city=o["city"], location_province=o["province"],
            is_available=True,
        ))
        print(f"  ✓ {o['name']}")
    db.commit()

    # ── 4. RESERVAS ───────────────────────────────────────────────────────────
    print("\n[4/7] Reservas...")
    bookings_data = [
        # cliente@demo.com — reservas sobre máquinas de david (para la demo)
        {"user": cliente, "mach": m_david_excav,  "start": now - timedelta(days=5),  "end": now + timedelta(days=2),  "status": BookingStatus.CONFIRMED,  "notes": "Cimentación parcela industrial en Lleida. Confirmar hora de llegada."},
        {"user": cliente, "mach": m_david_retro,  "start": now + timedelta(days=10), "end": now + timedelta(days=15), "status": BookingStatus.PENDING,    "notes": "Zanja de saneamiento en urbanización Pardinyes."},
        # Completadas (pasado)
        {"user": carlos,  "mach": m_excav_oliva,  "start": now - timedelta(days=45), "end": now - timedelta(days=38), "status": BookingStatus.COMPLETED,  "notes": "Cimentación de nave industrial en Castelldefels. Todo perfecto."},
        {"user": maria,   "mach": m_grua_medina,  "start": now - timedelta(days=30), "end": now - timedelta(days=22), "status": BookingStatus.COMPLETED,  "notes": "Edificio residencial de 8 plantas en Pozuelo. Sin incidencias."},
        # Confirmadas
        {"user": javier,  "mach": m_compact,      "start": now - timedelta(days=2),  "end": now + timedelta(days=5),  "status": BookingStatus.CONFIRMED,  "notes": "Urbanización sector norte Valencia."},
        {"user": ana,     "mach": m_carretilla,   "start": now + timedelta(days=3),  "end": now + timedelta(days=10), "status": BookingStatus.CONFIRMED,  "notes": "Almacén logístico en Sevilla Este."},
        {"user": carlos,  "mach": m_dumper_med,   "start": now + timedelta(days=7),  "end": now + timedelta(days=14), "status": BookingStatus.CONFIRMED,  "notes": "Obras de saneamiento en Parla."},
        # Pendientes
        {"user": maria,   "mach": m_mini,         "start": now + timedelta(days=12), "end": now + timedelta(days=16), "status": BookingStatus.PENDING,    "notes": "Reforma interior de local comercial."},
        {"user": javier,  "mach": m_excav_roca,   "start": now + timedelta(days=20), "end": now + timedelta(days=27), "status": BookingStatus.PENDING,    "notes": "Excavación de piscina en Marbella."},
        # Cancelada
        {"user": ana,     "mach": m_retro_oliva,  "start": now - timedelta(days=15), "end": now - timedelta(days=10), "status": BookingStatus.CANCELLED,  "notes": "Proyecto cancelado por el cliente final."},
    ]

    bookings = []
    for b in bookings_data:
        existing = db.query(Booking).filter(
            Booking.user_id == b["user"].id,
            Booking.machinery_id == b["mach"].id,
            Booking.status == b["status"],
        ).first()
        if existing:
            print(f"  ↳ {b['user'].full_name} / {b['mach'].title}")
            bookings.append(existing)
            continue
        days = max(1, (b["end"] - b["start"]).days)
        rate = b["mach"].daily_rate
        sub  = rate * days
        obj  = Booking(
            user_id=b["user"].id, machinery_id=b["mach"].id,
            start_date=b["start"], end_date=b["end"],
            daily_rate=rate, total_days=days,
            subtotal=sub, delivery_cost=0.0, insurance_cost=0.0,
            total_cost=sub, deposit_paid=0.0,
            status=b["status"], notes=b.get("notes"),
            confirmed_at=now - timedelta(days=1) if b["status"] in (BookingStatus.CONFIRMED, BookingStatus.COMPLETED) else None,
            completed_at=now - timedelta(days=1) if b["status"] == BookingStatus.COMPLETED else None,
            cancelled_at=now - timedelta(days=5) if b["status"] == BookingStatus.CANCELLED else None,
        )
        db.add(obj)
        db.flush()
        bookings.append(obj)
        print(f"  ✓ {b['user'].full_name} → {b['mach'].title} [{b['status'].value}]")
    db.commit()

    # ── 5. REVIEWS ────────────────────────────────────────────────────────────
    print("\n[5/7] Reviews...")
    reviews_data = [
        {"reviewer": carlos,  "type": TargetType.MACHINERY, "target_id": m_excav_oliva.id, "bid": next((bk.id for bk in bookings if bk.machinery_id == m_excav_oliva.id and bk.user_id == carlos.id), None),  "rating": 5, "comment": "Máquina en estado impecable, sin ningún fallo. El equipo de Oliva SL es muy profesional. Totalmente recomendable."},
        {"reviewer": maria,   "type": TargetType.MACHINERY, "target_id": m_grua_medina.id,  "bid": next((bk.id for bk in bookings if bk.machinery_id == m_grua_medina.id  and bk.user_id == maria.id),  None),  "rating": 5, "comment": "Grúa perfecta. Fernando, el gruista asignado, es un auténtico profesional. Montaje y desmontaje en tiempo récord."},
        {"reviewer": carlos,  "type": TargetType.MACHINERY, "target_id": m_retro_oliva.id,  "bid": None, "rating": 4, "comment": "Buena retroexcavadora para trabajos de zanjeo. Pequeño retraso en entrega, pero el trato excelente."},
        {"reviewer": javier,  "type": TargetType.MACHINERY, "target_id": m_compact.id,      "bid": None, "rating": 4, "comment": "Compactadora muy manejable para base granular. Funcionó sin incidencias durante 5 días consecutivos."},
        {"reviewer": ana,     "type": TargetType.MACHINERY, "target_id": m_carretilla.id,   "bid": None, "rating": 5, "comment": "Carretilla eléctrica perfecta para nuestro almacén. Sin emisiones, silenciosa y con buena autonomía."},
        {"reviewer": cliente, "type": TargetType.MACHINERY, "target_id": m_david_excav.id,  "bid": None, "rating": 5, "comment": "Excavadora en perfecto estado. David fue muy atento y la entrega fue puntual. 100% recomendable."},
    ]

    for r in reviews_data:
        if db.query(Review).filter(
            Review.reviewer_id == r["reviewer"].id,
            Review.target_type == r["type"],
            Review.target_id == r["target_id"],
        ).first():
            print(f"  ↳ {r['reviewer'].full_name}")
            continue
        db.add(Review(
            reviewer_id=r["reviewer"].id, target_type=r["type"],
            target_id=r["target_id"], booking_id=r.get("bid"),
            rating=r["rating"], comment=r["comment"],
        ))
        print(f"  ✓ {r['reviewer'].full_name} [{r['rating']}★] → máquina {r['target_id']}")
    db.commit()

    # ── 6. MENSAJES DE CHAT ───────────────────────────────────────────────────
    print("\n[6/7] Mensajes...")
    messages_data = [
        # cliente → david sobre la excavadora
        {"sender": cliente, "receiver": david, "mach": m_david_excav,
         "content": "Hola David, me interesa la excavadora CAT 320 GC. ¿Está disponible del 1 al 8 del mes que viene? ¿Incluye operario?"},
        {"sender": david,   "receiver": cliente, "mach": m_david_excav,
         "content": "Hola! Sí, está disponible. Incluye a Marc, nuestro operador con 12 años de experiencia. El transporte al punto de obra cuesta 150 €. ¿Cuál es la ubicación exacta?"},
        {"sender": cliente, "receiver": david, "mach": m_david_excav,
         "content": "Perfecto. Es en el Polígono Industrial Pla de l'Aigua, Lleida. Confirmo la reserva. Gracias!"},
        # cliente → david sobre la retroexcavadora
        {"sender": cliente, "receiver": david, "mach": m_david_retro,
         "content": "Buenos días David. ¿La retroexcavadora JCB tiene disponibilidad para la semana del 20? Necesito hacer unas zanjas de saneamiento."},
        {"sender": david,   "receiver": cliente, "mach": m_david_retro,
         "content": "Buenos días! Sí, queda libre esa semana. Te paso presupuesto: 300 €/día, depósito 1.500 €. ¿Te envío el contrato?"},
    ]

    for msg in messages_data:
        exists = db.query(Message).filter(
            Message.sender_id == msg["sender"].id,
            Message.receiver_id == msg["receiver"].id,
            Message.machinery_id == msg["mach"].id,
            Message.content == msg["content"],
        ).first()
        if exists:
            print(f"  ↳ {msg['sender'].full_name} → {msg['receiver'].full_name}")
            continue
        db.add(Message(
            sender_id=msg["sender"].id,
            receiver_id=msg["receiver"].id,
            machinery_id=msg["mach"].id,
            content=msg["content"],
            is_read=False,
        ))
        print(f"  ✓ {msg['sender'].full_name} → {msg['receiver'].full_name}: {msg['content'][:40]}…")
    db.commit()

    # ── 7. PETICIONES DE MAQUINARIA ───────────────────────────────────────────
    print("\n[7/7] Peticiones de maquinaria...")
    requests_data = [
        {"user": cliente, "type": MachineryType.EXCAVADORA,             "city": "Lleida",              "province": "Lleida",    "start": now + timedelta(days=14), "end": now + timedelta(days=21), "budget": 400, "desc": "Excavadora mínimo 15 t para cimentación de nave logística en Lleida. Operario titulado necesario."},
        {"user": carlos,  "type": MachineryType.EXCAVADORA,             "city": "Castelldefels",       "province": "Barcelona", "start": now + timedelta(days=14), "end": now + timedelta(days=28), "budget": 400, "desc": "Excavadora mínimo 18 t para cimentación de nave industrial. Terreno arcilloso. Transporte incluido preferible."},
        {"user": maria,   "type": MachineryType.GRUA_TORRE,             "city": "Majadahonda",         "province": "Madrid",    "start": now + timedelta(days=21), "end": now + timedelta(days=56), "budget": 550, "desc": "Grúa torre para edificio de 12 plantas. Pluma mínima 40 m, altura libre 28 m. Operario titulado necesario."},
        {"user": javier,  "type": MachineryType.COMPACTADORA,           "city": "Paterna",             "province": "Valencia",  "start": now + timedelta(days=10), "end": now + timedelta(days=17), "budget": 200, "desc": "Compactadora vibratoria para base de aparcamiento (2.500 m²). Peso 1-3 t."},
        {"user": ana,     "type": MachineryType.PLATAFORMA_ELEVADORA,   "city": "Mairena del Aljarafe","province": "Sevilla",   "start": now + timedelta(days=30), "end": now + timedelta(days=44), "budget": 250, "desc": "Plataforma articulada para pintura exterior en edificio de 4 plantas. Altura mínima 16 m."},
    ]

    for r in requests_data:
        if db.query(MachineryRequest).filter(
            MachineryRequest.user_id == r["user"].id,
            MachineryRequest.machinery_type == r["type"],
            MachineryRequest.city == r["city"],
        ).first():
            print(f"  ↳ {r['type'].value} en {r['city']}")
            continue
        db.add(MachineryRequest(
            user_id=r["user"].id, machinery_type=r["type"],
            description=r["desc"], city=r["city"], province=r["province"],
            start_date=r["start"], end_date=r["end"],
            budget_per_day=float(r["budget"]), status=RequestStatus.OPEN,
        ))
        print(f"  ✓ {r['type'].value} en {r['city']}")
    db.commit()
    db.close()

    print(f"\n{'='*60}")
    print(f"  Seed completado — entorno '{args.env}'")
    print(f"  Credenciales demo:")
    print(f"    Propietario : david@demo.com   / Demo1234!")
    print(f"    Cliente     : cliente@demo.com / Demo1234!")
    print(f"    Admin       : admin@demo.com   / Demo1234!")
    print(f"  12 usuarios · 15 máquinas (con fotos) · 10 operarios")
    print(f"  10 reservas · 6 reviews · 5 peticiones · 5 mensajes")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
