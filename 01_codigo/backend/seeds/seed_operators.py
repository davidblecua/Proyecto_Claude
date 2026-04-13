"""
Seed: 15 operarios de prueba con datos realistas para España

Uso:
    cd 01_codigo/backend
    python -m seeds.seed_operators

Es idempotente: comprueba por (name + location_city) antes de insertar.
No duplica si se ejecuta varias veces.
"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal
from app.models.user import User, UserRole
from app.models.operator import Operator
from app.models import machinery as _m  # noqa: registrar tablas
from app.models import booking as _b    # noqa
from app.models import message as _msg  # noqa
from app.core.security import get_password_hash


# ── Usuario propietario de los operarios de prueba ───────────────────────────

DEMO_OWNER = {
    "email": "operarios@rentamaq.com",
    "username": "rentamaq_operarios",
    "hashed_password": get_password_hash("Operarios2024!"),
    "full_name": "RentaMaq Operarios Demo",
    "role": UserRole.PUBLISHER,
    "is_active": True,
    "is_verified": True,
}


# ── 15 operarios de prueba ────────────────────────────────────────────────────

OPERATORS = [
    {
        "name": "Carlos Martínez Ruiz",
        "description": "Operador de excavadora con más de 15 años de experiencia en obras civiles y movimiento de tierras. Especializado en Caterpillar y Komatsu.",
        "daily_rate": 320.0,
        "experience_years": 15,
        "phone": "612 345 678",
        "machine_skills": json.dumps(["excavadora", "retroexcavadora", "bulldozer"]),
        "location_city": "Madrid",
        "location_province": "Madrid",
        "is_available": True,
        "photo_url": "https://i.pravatar.cc/150?img=1",
    },
    {
        "name": "Javier López García",
        "description": "Gruista certificado con experiencia en grúas torre y camión grúa. Ha trabajado en más de 50 obras de edificación residencial y comercial.",
        "daily_rate": 380.0,
        "experience_years": 12,
        "phone": "623 456 789",
        "machine_skills": json.dumps(["grua_torre", "camion_grua", "plataforma_elevadora"]),
        "location_city": "Barcelona",
        "location_province": "Barcelona",
        "is_available": True,
        "photo_url": "https://i.pravatar.cc/150?img=2",
    },
    {
        "name": "Antonio Fernández Moreno",
        "description": "Conductor de dumper y pala cargadora. Carné C+E y experiencia en canteras y construcción de carreteras.",
        "daily_rate": 280.0,
        "experience_years": 8,
        "phone": "634 567 890",
        "machine_skills": json.dumps(["dumper", "pala_cargadora", "compactadora"]),
        "location_city": "Valencia",
        "location_province": "Valencia",
        "is_available": True,
        "photo_url": "https://i.pravatar.cc/150?img=3",
    },
    {
        "name": "Manuel Sánchez Torres",
        "description": "Especialista en plataformas elevadoras y manipuladores telescópicos. Certificado IPAF. Trabaja principalmente en trabajos en altura.",
        "daily_rate": 260.0,
        "experience_years": 6,
        "phone": "645 678 901",
        "machine_skills": json.dumps(["plataforma_elevadora", "manipulador_telescopico", "carretilla_elevadora"]),
        "location_city": "Sevilla",
        "location_province": "Sevilla",
        "is_available": True,
        "photo_url": "https://i.pravatar.cc/150?img=4",
    },
    {
        "name": "Francisco Jiménez Díaz",
        "description": "Operador de motoniveladora y compactadora con 20 años de experiencia en construcción de carreteras y explanaciones.",
        "daily_rate": 350.0,
        "experience_years": 20,
        "phone": "656 789 012",
        "machine_skills": json.dumps(["motoniveladora", "compactadora", "bulldozer"]),
        "location_city": "Bilbao",
        "location_province": "Vizcaya",
        "is_available": True,
        "photo_url": "https://i.pravatar.cc/150?img=5",
    },
    {
        "name": "José Romero Alonso",
        "description": "Operador de retroexcavadora con amplia experiencia en demoliciones y excavaciones en entornos urbanos. Gran precisión.",
        "daily_rate": 300.0,
        "experience_years": 10,
        "phone": "667 890 123",
        "machine_skills": json.dumps(["retroexcavadora", "martillo_hidraulico", "excavadora"]),
        "location_city": "Zaragoza",
        "location_province": "Zaragoza",
        "is_available": True,
        "photo_url": "https://i.pravatar.cc/150?img=6",
    },
    {
        "name": "Luis González Navarro",
        "description": "Carretillero y operador de montacargas. Amplia experiencia en logística de obra y almacenes industriales.",
        "daily_rate": 200.0,
        "experience_years": 5,
        "phone": "678 901 234",
        "machine_skills": json.dumps(["carretilla_elevadora", "montacargas", "manipulador_telescopico"]),
        "location_city": "Málaga",
        "location_province": "Málaga",
        "is_available": True,
        "photo_url": "https://i.pravatar.cc/150?img=7",
    },
    {
        "name": "Miguel Pérez Serrano",
        "description": "Especialista en bombas de hormigón y hormigoneras. Experiencia en grandes obras de infraestructura y edificación.",
        "daily_rate": 290.0,
        "experience_years": 9,
        "phone": "689 012 345",
        "machine_skills": json.dumps(["bomba_hormigon", "hormigonera"]),
        "location_city": "Murcia",
        "location_province": "Murcia",
        "is_available": True,
        "photo_url": "https://i.pravatar.cc/150?img=8",
    },
    {
        "name": "Alejandro Ramírez Castro",
        "description": "Operador de cortadora de asfalto y martillo hidráulico. Especializado en demolición selectiva y rehabilitación de pavimentos.",
        "daily_rate": 240.0,
        "experience_years": 7,
        "phone": "690 123 456",
        "machine_skills": json.dumps(["cortadora_asfalto", "martillo_hidraulico", "compactadora"]),
        "location_city": "Palma de Mallorca",
        "location_province": "Baleares",
        "is_available": True,
        "photo_url": "https://i.pravatar.cc/150?img=9",
    },
    {
        "name": "David Ortiz Vega",
        "description": "Operador de bulldozer con certificación para trabajos en zonas de difícil acceso y taludes. Experiencia minera.",
        "daily_rate": 370.0,
        "experience_years": 14,
        "phone": "601 234 567",
        "machine_skills": json.dumps(["bulldozer", "motoniveladora", "pala_cargadora"]),
        "location_city": "Oviedo",
        "location_province": "Asturias",
        "is_available": True,
        "photo_url": "https://i.pravatar.cc/150?img=10",
    },
    {
        "name": "Pablo Herrero Blanco",
        "description": "Especialista en montaje y operación de andamios y plataformas para fachadas. Formación en trabajos en altura y PRL.",
        "daily_rate": 180.0,
        "experience_years": 4,
        "phone": "612 987 654",
        "machine_skills": json.dumps(["andamio", "plataforma_elevadora"]),
        "location_city": "Valladolid",
        "location_province": "Valladolid",
        "is_available": True,
        "photo_url": "https://i.pravatar.cc/150?img=11",
    },
    {
        "name": "Roberto Molina Flores",
        "description": "Técnico en generadores y compresores industriales. Mantenimiento preventivo y operación en obra para trabajos eléctricos y neumáticos.",
        "daily_rate": 220.0,
        "experience_years": 11,
        "phone": "623 876 543",
        "machine_skills": json.dumps(["generador", "compresor"]),
        "location_city": "Las Palmas de Gran Canaria",
        "location_province": "Las Palmas",
        "is_available": True,
        "photo_url": "https://i.pravatar.cc/150?img=12",
    },
    {
        "name": "Fernando Guerrero Rubio",
        "description": "Gruista especializado en grúas torre de gran altura. Más de 18 años en el sector de la construcción de rascacielos y grandes estructuras.",
        "daily_rate": 420.0,
        "experience_years": 18,
        "phone": "634 765 432",
        "machine_skills": json.dumps(["grua_torre", "camion_grua"]),
        "location_city": "Santander",
        "location_province": "Cantabria",
        "is_available": True,
        "photo_url": "https://i.pravatar.cc/150?img=13",
    },
    {
        "name": "Sergio Iglesias Peña",
        "description": "Operador polivalente con experiencia en múltiples tipos de maquinaria. Apto para obras de gran envergadura donde se requiere flexibilidad.",
        "daily_rate": 310.0,
        "experience_years": 13,
        "phone": "645 654 321",
        "machine_skills": json.dumps(["excavadora", "pala_cargadora", "dumper", "compactadora"]),
        "location_city": "Pamplona",
        "location_province": "Navarra",
        "is_available": True,
        "photo_url": "https://i.pravatar.cc/150?img=14",
    },
    {
        "name": "Raúl Vargas Medina",
        "description": "Operador de excavadora hidráulica especializado en obras de saneamiento y redes de servicios. Experiencia en entornos urbanos.",
        "daily_rate": 270.0,
        "experience_years": 7,
        "phone": "656 543 210",
        "machine_skills": json.dumps(["excavadora", "retroexcavadora"]),
        "location_city": "Vitoria-Gasteiz",
        "location_province": "Álava",
        "is_available": True,
        "photo_url": "https://i.pravatar.cc/150?img=15",
    },
]


def run():
    db = SessionLocal()
    try:
        # 1. Obtener o crear usuario propietario
        owner = db.query(User).filter(User.email == DEMO_OWNER["email"]).first()
        if not owner:
            owner = User(**DEMO_OWNER)
            db.add(owner)
            db.flush()
            print(f"  Usuario creado: {owner.email}")
        else:
            print(f"  Usuario ya existe: {owner.email}")

        # 2. Insertar operarios (idempotente por nombre+ciudad)
        inserted = 0
        skipped = 0
        for op_data in OPERATORS:
            existing = (
                db.query(Operator)
                .filter(
                    Operator.name == op_data["name"],
                    Operator.location_city == op_data["location_city"],
                )
                .first()
            )
            if existing:
                skipped += 1
                continue

            op = Operator(
                owner_id=owner.id,
                name=op_data["name"],
                description=op_data["description"],
                daily_rate=op_data["daily_rate"],
                experience_years=op_data["experience_years"],
                phone=op_data["phone"],
                machine_skills=op_data["machine_skills"],
                location_city=op_data["location_city"],
                location_province=op_data["location_province"],
                is_available=op_data["is_available"],
            )
            db.add(op)
            inserted += 1

        db.commit()
        print(f"\n  Operarios insertados: {inserted}")
        print(f"  Operarios ya existentes (omitidos): {skipped}")
        print(f"  Total en BD: {db.query(Operator).count()}")

    except Exception as e:
        db.rollback()
        print(f"ERROR: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("Insertando operarios de prueba...")
    run()
    print("Listo.")
