"""
Script de inicialización de base de datos
Crea las tablas y opcionalmente datos de prueba
"""
from app.db.database import engine, Base, SessionLocal
from app.models.user import User, UserRole
from app.models.machinery import Machinery, MachineryType, MachineryCondition
from app.models.booking import Booking
from app.core.security import get_password_hash
from datetime import datetime, timedelta
import json


def init_db():
    """Inicializa la base de datos creando todas las tablas"""
    print("🔧 Creando tablas en la base de datos...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas creadas correctamente")


def create_sample_data():
    """Crea datos de muestra para desarrollo/testing"""
    db = SessionLocal()
    
    try:
        print("📝 Creando datos de muestra...")
        
        # Crear usuarios de prueba
        admin_user = User(
            email="admin@rentamaq.com",
            username="admin",
            hashed_password=get_password_hash("Admin123!"),
            full_name="Administrador RentaMaq",
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True,
            company_name="RentaMaq S.L.",
            phone="+34 600 000 001"
        )
        
        publisher_user = User(
            email="empresa@construcciones.com",
            username="construcciones_sa",
            hashed_password=get_password_hash("Publisher123!"),
            full_name="Juan Martínez",
            role=UserRole.PUBLISHER,
            is_active=True,
            is_verified=True,
            company_name="Construcciones García S.A.",
            tax_id="B12345678",
            phone="+34 600 000 002",
            address="Calle Mayor 123, Madrid"
        )
        
        consumer_user = User(
            email="cliente@ejemplo.com",
            username="cliente_ejemplo",
            hashed_password=get_password_hash("Consumer123!"),
            full_name="María López",
            role=UserRole.CONSUMER,
            is_active=True,
            is_verified=True,
            phone="+34 600 000 003"
        )
        
        db.add_all([admin_user, publisher_user, consumer_user])
        db.commit()
        db.refresh(publisher_user)
        
        print("✅ Usuarios de prueba creados")
        print(f"   - Admin: admin@rentamaq.com / Admin123!")
        print(f"   - Publisher: empresa@construcciones.com / Publisher123!")
        print(f"   - Consumer: cliente@ejemplo.com / Consumer123!")
        
        # Crear maquinaria de muestra
        machinery_samples = [
            {
                "title": "Excavadora Caterpillar 320D",
                "description": "Excavadora hidráulica de 20 toneladas en excelente estado. Ideal para excavaciones profundas y movimiento de tierra. Incluye martillo hidráulico.",
                "machinery_type": MachineryType.EXCAVADORA,
                "brand": "Caterpillar",
                "model": "320D",
                "year": 2020,
                "condition": MachineryCondition.EXCELENTE,
                "capacity": "20 toneladas",
                "weight": 20000,
                "fuel_type": "Diésel",
                "daily_rate": 250.0,
                "weekly_rate": 1400.0,
                "monthly_rate": 5000.0,
                "deposit": 2000.0,
                "location_city": "Madrid",
                "location_province": "Madrid",
                "delivery_available": True,
                "delivery_cost": 150.0,
                "requires_operator": False,
                "insurance_included": False
            },
            {
                "title": "Grúa Torre Potain MDT 219",
                "description": "Grúa torre de gran altura con capacidad de carga de 10 toneladas. Perfecta para construcción de edificios de varias plantas.",
                "machinery_type": MachineryType.GRUA_TORRE,
                "brand": "Potain",
                "model": "MDT 219",
                "year": 2019,
                "condition": MachineryCondition.BUENO,
                "capacity": "10 toneladas",
                "daily_rate": 400.0,
                "weekly_rate": 2400.0,
                "monthly_rate": 8500.0,
                "deposit": 5000.0,
                "location_city": "Barcelona",
                "location_province": "Barcelona",
                "delivery_available": True,
                "delivery_cost": 300.0,
                "requires_operator": True,
                "requires_license": True,
                "insurance_included": True
            },
            {
                "title": "Dumper Ausa D350",
                "description": "Dumper compacto de 3.5 toneladas. Ideal para transporte de materiales en obras pequeñas y medianas. Muy maniobrable.",
                "machinery_type": MachineryType.DUMPER,
                "brand": "Ausa",
                "model": "D350",
                "year": 2021,
                "condition": MachineryCondition.EXCELENTE,
                "capacity": "3.5 toneladas",
                "weight": 2500,
                "fuel_type": "Diésel",
                "daily_rate": 80.0,
                "weekly_rate": 450.0,
                "monthly_rate": 1600.0,
                "deposit": 500.0,
                "location_city": "Valencia",
                "location_province": "Valencia",
                "delivery_available": True,
                "delivery_cost": 100.0,
                "requires_operator": False
            },
            {
                "title": "Plataforma Elevadora Genie Z-45",
                "description": "Plataforma elevadora articulada de 15 metros de altura. Perfecta para trabajos en altura.",
                "machinery_type": MachineryType.PLATAFORMA_ELEVADORA,
                "brand": "Genie",
                "model": "Z-45",
                "year": 2022,
                "condition": MachineryCondition.EXCELENTE,
                "capacity": "230 kg",
                "daily_rate": 120.0,
                "weekly_rate": 650.0,
                "monthly_rate": 2200.0,
                "deposit": 1000.0,
                "location_city": "Sevilla",
                "location_province": "Sevilla",
                "delivery_available": True,
                "delivery_cost": 80.0,
                "requires_license": True,
                "insurance_included": True
            },
            {
                "title": "Compactadora Bomag BW 120",
                "description": "Rodillo compactador vibratorio de 12 toneladas. Ideal para compactación de suelos y asfalto.",
                "machinery_type": MachineryType.COMPACTADORA,
                "brand": "Bomag",
                "model": "BW 120",
                "year": 2018,
                "condition": MachineryCondition.BUENO,
                "capacity": "12 toneladas",
                "weight": 12000,
                "fuel_type": "Diésel",
                "daily_rate": 180.0,
                "weekly_rate": 1000.0,
                "monthly_rate": 3500.0,
                "deposit": 1500.0,
                "location_city": "Bilbao",
                "location_province": "Vizcaya",
                "delivery_available": False,
                "requires_operator": False
            }
        ]
        
        for machinery_data in machinery_samples:
            machinery = Machinery(**machinery_data, owner_id=publisher_user.id)
            db.add(machinery)
        
        db.commit()
        print(f"✅ {len(machinery_samples)} máquinas de muestra creadas")
        
        print("\n🎉 Datos de muestra creados exitosamente")
        
    except Exception as e:
        print(f"❌ Error creando datos de muestra: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("🚀 Inicializando base de datos...")
    print("-" * 50)
    
    init_db()
    
    response = input("\n¿Deseas crear datos de muestra? (s/n): ")
    if response.lower() == 's':
        create_sample_data()
    
    print("\n✅ Proceso completado")