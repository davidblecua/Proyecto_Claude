"""
Seed: 30 modelos de maquinaria pesada mas usados en construccion
Fuentes: Equipment World, Komatsu Colombia, CAT.com, BuscaMaquinaria, JCB.com

Uso:
    cd 01_codigo/backend
    python -m seeds.seed_30_machinery

Requiere que la BD este inicializada (tablas creadas).
Crea un usuario catalogo 'RentaMaq Catalogo' si no existe y
añade los 30 registros de maquinaria. Es idempotente: no duplica
si ya existen registros con el mismo titulo.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal
from app.models.user import User, UserRole
from app.models.machinery import Machinery, MachineryType, MachineryCondition
from app.models import booking, message, operator  # noqa: registrar en metadata
from app.core.security import get_password_hash


# ── Usuario catalogo ──────────────────────────────────────────────────────────

CATALOG_USER = {
    "email": "catalogo@rentamaq.com",
    "username": "rentamaq_catalogo",
    "hashed_password": get_password_hash("Catalogo2024!"),
    "full_name": "RentaMaq Catalogo",
    "role": UserRole.PUBLISHER,
    "is_active": True,
    "is_verified": True,
    "company_name": "RentaMaq S.L.",
    "phone": "+34 900 000 000",
}

# ── 30 modelos reales de maquinaria pesada ─────────────────────────────────────
# Fuentes consultadas:
#   - Equipment World "Best-Selling Construction Equipment 2024"
#   - Komatsu Colombia "Maquinaria para construccion: Modelos y caracteristicas"
#   - CAT.com catalogo oficial
#   - JCB.com productos oficiales
#   - BuscaMaquinaria "15 Equipos Pesados mas importantes en Construccion"

MACHINERY_SEED = [

    # ── 1. Excavadoras ────────────────────────────────────────────────────────
    {
        "title": "Excavadora Caterpillar 320 GC",
        "description": (
            "La CAT 320 GC es la excavadora hidraulica mas vendida del mundo. "
            "20 t de peso operativo, motor C4.4 de 121 kW, brazo de 5.7 m. "
            "Ideal para excavacion general, carga de camiones y demolicion ligera. "
            "Sistema Cat Connect para monitoreo remoto incluido."
        ),
        "machinery_type": MachineryType.EXCAVADORA,
        "brand": "Caterpillar",
        "model": "320 GC",
        "year": 2022,
        "condition": MachineryCondition.EXCELENTE,
        "capacity": "20 t",
        "weight": 20500,
        "fuel_type": "Diesel",
        "daily_rate": 260.0,
        "weekly_rate": 1500.0,
        "monthly_rate": 5200.0,
        "deposit": 2000.0,
        "location_city": "Madrid",
        "location_province": "Madrid",
        "delivery_available": True,
        "delivery_cost": 150.0,
        "requires_operator": False,
        "insurance_included": False,
    },
    {
        "title": "Excavadora Komatsu PC210LC-11",
        "description": (
            "Komatsu PC210LC-11 de 21.3 t con motor SAA6D107E-3 de 122 kW. "
            "Sistema inteligente de gestion de combustible KOMTRAX. "
            "Brazo largo para excavaciones profundas en zanjas y cimentaciones. "
            "Cabina con certificacion ROPS/FOPS nivel II."
        ),
        "machinery_type": MachineryType.EXCAVADORA,
        "brand": "Komatsu",
        "model": "PC210LC-11",
        "year": 2021,
        "condition": MachineryCondition.EXCELENTE,
        "capacity": "21.3 t",
        "weight": 21300,
        "fuel_type": "Diesel",
        "daily_rate": 250.0,
        "weekly_rate": 1450.0,
        "monthly_rate": 5000.0,
        "deposit": 2000.0,
        "location_city": "Barcelona",
        "location_province": "Barcelona",
        "delivery_available": True,
        "delivery_cost": 200.0,
        "requires_operator": False,
        "insurance_included": False,
    },

    # ── 2. Retroexcavadoras ───────────────────────────────────────────────────
    {
        "title": "Retroexcavadora JCB 3CX",
        "description": (
            "La JCB 3CX es la retroexcavadora mas vendida en el mundo (50% del mercado). "
            "Motor JCB EcoMAX de 81 kW, traccion 4x4, pala cargadora de 1.3 m3. "
            "Perfecta para zanjas, instalacion de tuberias y trabajos urbanos. "
            "Muy maniobrable en espacios reducidos."
        ),
        "machinery_type": MachineryType.RETROEXCAVADORA,
        "brand": "JCB",
        "model": "3CX",
        "year": 2022,
        "condition": MachineryCondition.EXCELENTE,
        "capacity": "1.3 m3",
        "weight": 8350,
        "fuel_type": "Diesel",
        "daily_rate": 180.0,
        "weekly_rate": 1000.0,
        "monthly_rate": 3500.0,
        "deposit": 1500.0,
        "location_city": "Valencia",
        "location_province": "Valencia",
        "delivery_available": True,
        "delivery_cost": 100.0,
        "requires_operator": False,
        "insurance_included": False,
    },
    {
        "title": "Retroexcavadora Caterpillar 420F2",
        "description": (
            "CAT 420F2 con motor C4.4 ACERT de 82 kW. "
            "Profundidad maxima de excavacion 5.8 m, cuchara trasera de 0.08-0.29 m3. "
            "Ideal para obras de saneamiento, instalacion de cables y demolicion. "
            "Sistema Cat Product Link para telemetria."
        ),
        "machinery_type": MachineryType.RETROEXCAVADORA,
        "brand": "Caterpillar",
        "model": "420F2",
        "year": 2021,
        "condition": MachineryCondition.BUENO,
        "capacity": "0.29 m3",
        "weight": 8700,
        "fuel_type": "Diesel",
        "daily_rate": 170.0,
        "weekly_rate": 950.0,
        "monthly_rate": 3300.0,
        "deposit": 1500.0,
        "location_city": "Sevilla",
        "location_province": "Sevilla",
        "delivery_available": True,
        "delivery_cost": 120.0,
        "requires_operator": False,
        "insurance_included": False,
    },

    # ── 3. Bulldozers ─────────────────────────────────────────────────────────
    {
        "title": "Bulldozer Caterpillar D6T XL",
        "description": (
            "CAT D6T XL con motor Cat C9.3B de 175 kW. "
            "Hoja recta de 3.5 m de ancho para desbroce y nivelacion de terrenos. "
            "Sistema de seguimiento electronico Cat GRADE. "
            "Ideal para preparacion de solares, terraplenes y explanaciones."
        ),
        "machinery_type": MachineryType.BULLDOZER,
        "brand": "Caterpillar",
        "model": "D6T XL",
        "year": 2020,
        "condition": MachineryCondition.BUENO,
        "capacity": "3.5 m hoja",
        "weight": 19800,
        "fuel_type": "Diesel",
        "daily_rate": 320.0,
        "weekly_rate": 1800.0,
        "monthly_rate": 6500.0,
        "deposit": 3000.0,
        "location_city": "Zaragoza",
        "location_province": "Zaragoza",
        "delivery_available": True,
        "delivery_cost": 250.0,
        "requires_operator": True,
        "insurance_included": False,
    },
    {
        "title": "Bulldozer Komatsu D65EX-18",
        "description": (
            "Komatsu D65EX-18 con motor SAA6D114E-6 de 168 kW. "
            "Hoja semiuniversal de 3.46 m, ripper monotina trasero opcional. "
            "Sistema KOMTRAX Plus para gestion de flota. "
            "Alto rendimiento en movimiento de tierras y rellenos compactados."
        ),
        "machinery_type": MachineryType.BULLDOZER,
        "brand": "Komatsu",
        "model": "D65EX-18",
        "year": 2020,
        "condition": MachineryCondition.BUENO,
        "capacity": "3.46 m hoja",
        "weight": 19100,
        "fuel_type": "Diesel",
        "daily_rate": 310.0,
        "weekly_rate": 1750.0,
        "monthly_rate": 6200.0,
        "deposit": 3000.0,
        "location_city": "Bilbao",
        "location_province": "Vizcaya",
        "delivery_available": True,
        "delivery_cost": 280.0,
        "requires_operator": True,
        "insurance_included": False,
    },

    # ── 4. Palas Cargadoras ───────────────────────────────────────────────────
    {
        "title": "Pala Cargadora Volvo L120H",
        "description": (
            "Volvo L120H con motor Volvo D8J de 185 kW. "
            "Cubo de 3.0 m3, carga de punta 11.500 kg. "
            "Transmision automatica de 4 velocidades, direccion articulada. "
            "Optima para carga de materiales en canteras y obras de carretera."
        ),
        "machinery_type": MachineryType.PALA_CARGADORA,
        "brand": "Volvo",
        "model": "L120H",
        "year": 2021,
        "condition": MachineryCondition.EXCELENTE,
        "capacity": "3.0 m3",
        "weight": 20000,
        "fuel_type": "Diesel",
        "daily_rate": 280.0,
        "weekly_rate": 1600.0,
        "monthly_rate": 5600.0,
        "deposit": 2500.0,
        "location_city": "Malaga",
        "location_province": "Malaga",
        "delivery_available": True,
        "delivery_cost": 180.0,
        "requires_operator": False,
        "insurance_included": False,
    },
    {
        "title": "Pala Cargadora Caterpillar 950 GC",
        "description": (
            "CAT 950 GC con motor Cat C7.1 ACERT de 162 kW. "
            "Cubo de 2.7 m3, fuerza de arranque de 150 kN. "
            "Sistema Z-bar para ciclos rapidos. "
            "Excelente para carga de camiones, limpieza de solar y segregacion."
        ),
        "machinery_type": MachineryType.PALA_CARGADORA,
        "brand": "Caterpillar",
        "model": "950 GC",
        "year": 2021,
        "condition": MachineryCondition.EXCELENTE,
        "capacity": "2.7 m3",
        "weight": 18200,
        "fuel_type": "Diesel",
        "daily_rate": 270.0,
        "weekly_rate": 1550.0,
        "monthly_rate": 5400.0,
        "deposit": 2500.0,
        "location_city": "Alicante",
        "location_province": "Alicante",
        "delivery_available": True,
        "delivery_cost": 170.0,
        "requires_operator": False,
        "insurance_included": False,
    },

    # ── 5. Dumpers ────────────────────────────────────────────────────────────
    {
        "title": "Dumper AUSA D600 AHG",
        "description": (
            "AUSA D600 AHG dumper compacto de 6 t, motor Deutz TD 2.9 L4. "
            "Traccion total 4x4, volteo hidraulico frontal. "
            "Ideal para transporte de escombros y materiales en obras urbanas. "
            "Radio de giro muy reducido para espacios confinados."
        ),
        "machinery_type": MachineryType.DUMPER,
        "brand": "AUSA",
        "model": "D600 AHG",
        "year": 2022,
        "condition": MachineryCondition.EXCELENTE,
        "capacity": "6 t / 3.6 m3",
        "weight": 4800,
        "fuel_type": "Diesel",
        "daily_rate": 110.0,
        "weekly_rate": 620.0,
        "monthly_rate": 2200.0,
        "deposit": 800.0,
        "location_city": "Murcia",
        "location_province": "Murcia",
        "delivery_available": True,
        "delivery_cost": 80.0,
        "requires_operator": False,
        "insurance_included": False,
    },
    {
        "title": "Dumper Thwaites Mach 574",
        "description": (
            "Thwaites Mach 574 de 5 t con motor Perkins 404F-22T de 41 kW. "
            "Cubo de volteo frontal de 0.5 m3. "
            "Muy utilizado en obras de edificacion y rehabilitacion. "
            "Compacto y maniobrable en interiores y patios de obra."
        ),
        "machinery_type": MachineryType.DUMPER,
        "brand": "Thwaites",
        "model": "Mach 574",
        "year": 2020,
        "condition": MachineryCondition.BUENO,
        "capacity": "5 t / 0.5 m3",
        "weight": 3500,
        "fuel_type": "Diesel",
        "daily_rate": 90.0,
        "weekly_rate": 500.0,
        "monthly_rate": 1800.0,
        "deposit": 600.0,
        "location_city": "Valladolid",
        "location_province": "Valladolid",
        "delivery_available": True,
        "delivery_cost": 90.0,
        "requires_operator": False,
        "insurance_included": False,
    },

    # ── 6. Hormigoneras ───────────────────────────────────────────────────────
    {
        "title": "Hormigonera Altrad H140",
        "description": (
            "Hormigonera de obra Altrad H140 de 140 litros de capacidad. "
            "Motor electrico de 1.1 kW, tambor de acero de alta durabilidad. "
            "La mas utilizada en obras de edificacion residencial en Espana. "
            "Bajo consumo y mantenimiento minimo."
        ),
        "machinery_type": MachineryType.HORMIGONERA,
        "brand": "Altrad",
        "model": "H140",
        "year": 2023,
        "condition": MachineryCondition.EXCELENTE,
        "capacity": "140 L",
        "weight": 85,
        "fuel_type": "Electrico",
        "daily_rate": 25.0,
        "weekly_rate": 130.0,
        "monthly_rate": 450.0,
        "deposit": 200.0,
        "location_city": "Granada",
        "location_province": "Granada",
        "delivery_available": True,
        "delivery_cost": 30.0,
        "requires_operator": False,
        "insurance_included": False,
    },
    {
        "title": "Hormigonera Belle Premier 130XT",
        "description": (
            "Belle Premier 130XT con motor Honda GX160 de gasolina 4.8 CV. "
            "Capacidad mezcladora de 130 L. "
            "Totalmente autonoma, sin necesidad de corriente electrica. "
            "Ideal para obras en zonas sin suministro electrico."
        ),
        "machinery_type": MachineryType.HORMIGONERA,
        "brand": "Belle",
        "model": "Premier 130XT",
        "year": 2022,
        "condition": MachineryCondition.BUENO,
        "capacity": "130 L",
        "weight": 72,
        "fuel_type": "Gasolina",
        "daily_rate": 28.0,
        "weekly_rate": 145.0,
        "monthly_rate": 490.0,
        "deposit": 200.0,
        "location_city": "Cordoba",
        "location_province": "Cordoba",
        "delivery_available": True,
        "delivery_cost": 30.0,
        "requires_operator": False,
        "insurance_included": False,
    },

    # ── 7. Camiones Grua ──────────────────────────────────────────────────────
    {
        "title": "Camion Grua Fassi F215A.2.26",
        "description": (
            "Fassi F215A.2.26 sobre camion, capacidad de izado 6.5 t·m. "
            "Alcance horizontal maximo de 9.3 m, 2 extensiones hidraulicas. "
            "El camion grua mas extendido en obras de construccion en Espana. "
            "Ideal para descarga de materiales y colocacion de prefabricados."
        ),
        "machinery_type": MachineryType.CAMION_GRUA,
        "brand": "Fassi",
        "model": "F215A.2.26",
        "year": 2020,
        "condition": MachineryCondition.BUENO,
        "capacity": "6.5 t·m",
        "fuel_type": "Diesel",
        "daily_rate": 350.0,
        "weekly_rate": 2000.0,
        "monthly_rate": 7000.0,
        "deposit": 3000.0,
        "location_city": "Madrid",
        "location_province": "Madrid",
        "delivery_available": False,
        "requires_operator": True,
        "requires_license": True,
        "insurance_included": True,
    },
    {
        "title": "Camion Grua Hiab X-HiPro 232",
        "description": (
            "Hiab X-HiPro 232 con capacidad de carga de 11.6 t·m. "
            "Alcance de 15 m con extensiones manuales. "
            "Control HiPro con joystick para maxima precision de izado. "
            "Muy usado en obras de rehabilitacion y edificacion en altura."
        ),
        "machinery_type": MachineryType.CAMION_GRUA,
        "brand": "Hiab",
        "model": "X-HiPro 232",
        "year": 2021,
        "condition": MachineryCondition.EXCELENTE,
        "capacity": "11.6 t·m",
        "fuel_type": "Diesel",
        "daily_rate": 420.0,
        "weekly_rate": 2400.0,
        "monthly_rate": 8500.0,
        "deposit": 4000.0,
        "location_city": "Barcelona",
        "location_province": "Barcelona",
        "delivery_available": False,
        "requires_operator": True,
        "requires_license": True,
        "insurance_included": True,
    },

    # ── 8. Gruas Torre ────────────────────────────────────────────────────────
    {
        "title": "Grua Torre Liebherr 81K.1",
        "description": (
            "Liebherr 81K.1 autoplegable, altura bajo gancho 40.6 m. "
            "Capacidad maxima de carga 6 t, alcance de trabajo 45 m. "
            "Montaje rapido en menos de 2 horas. "
            "La grua torre mas usada en edificacion residencial en Europa."
        ),
        "machinery_type": MachineryType.GRUA_TORRE,
        "brand": "Liebherr",
        "model": "81K.1",
        "year": 2019,
        "condition": MachineryCondition.BUENO,
        "capacity": "6 t",
        "daily_rate": 420.0,
        "weekly_rate": 2500.0,
        "monthly_rate": 9000.0,
        "deposit": 5000.0,
        "location_city": "Valencia",
        "location_province": "Valencia",
        "delivery_available": True,
        "delivery_cost": 800.0,
        "requires_operator": True,
        "requires_license": True,
        "insurance_included": True,
    },
    {
        "title": "Grua Torre Potain MDT 219 J10",
        "description": (
            "Potain MDT 219 J10 de alta capacidad, carga maxima 10 t. "
            "Altura bajo gancho hasta 54.6 m, pluma de 60 m. "
            "Sistema Crane Control System (CCS) para operacion precisa. "
            "Ideal para edificios de gran altura y obras industriales."
        ),
        "machinery_type": MachineryType.GRUA_TORRE,
        "brand": "Potain",
        "model": "MDT 219 J10",
        "year": 2020,
        "condition": MachineryCondition.BUENO,
        "capacity": "10 t",
        "daily_rate": 550.0,
        "weekly_rate": 3200.0,
        "monthly_rate": 11500.0,
        "deposit": 8000.0,
        "location_city": "Madrid",
        "location_province": "Madrid",
        "delivery_available": True,
        "delivery_cost": 1200.0,
        "requires_operator": True,
        "requires_license": True,
        "insurance_included": True,
    },

    # ── 9. Manipuladores Telescopicos ─────────────────────────────────────────
    {
        "title": "Manipulador Telescopico Merlo P40.17",
        "description": (
            "Merlo P40.17 con capacidad de carga 4 t y altura de elevacion 17 m. "
            "El mas extendido en obras de albañileria y prefabricados en Espana. "
            "Traccion total, directrices en 4 ruedas. "
            "Compatible con horquillas, cubilotes, cestas y plumas."
        ),
        "machinery_type": MachineryType.MANIPULADOR_TELESCOPICO,
        "brand": "Merlo",
        "model": "P40.17",
        "year": 2022,
        "condition": MachineryCondition.EXCELENTE,
        "capacity": "4 t / 17 m",
        "weight": 11500,
        "fuel_type": "Diesel",
        "daily_rate": 200.0,
        "weekly_rate": 1150.0,
        "monthly_rate": 4000.0,
        "deposit": 2000.0,
        "location_city": "Pamplona",
        "location_province": "Navarra",
        "delivery_available": True,
        "delivery_cost": 120.0,
        "requires_operator": False,
        "requires_license": True,
        "insurance_included": False,
    },
    {
        "title": "Manipulador Telescopico JLG 742",
        "description": (
            "JLG 742 con capacidad de 3.2 t y altura maxima de 12.8 m. "
            "Motor Deutz de 55 kW, 4 modos de direccion. "
            "Especialmente indicado para obras de construccion e industria. "
            "Estabilizadores traseros para trabajo en pendiente."
        ),
        "machinery_type": MachineryType.MANIPULADOR_TELESCOPICO,
        "brand": "JLG",
        "model": "742",
        "year": 2021,
        "condition": MachineryCondition.BUENO,
        "capacity": "3.2 t / 12.8 m",
        "weight": 8700,
        "fuel_type": "Diesel",
        "daily_rate": 180.0,
        "weekly_rate": 1000.0,
        "monthly_rate": 3500.0,
        "deposit": 1800.0,
        "location_city": "San Sebastian",
        "location_province": "Guipuzcoa",
        "delivery_available": True,
        "delivery_cost": 110.0,
        "requires_operator": False,
        "requires_license": True,
        "insurance_included": False,
    },

    # ── 10. Plataformas Elevadoras ────────────────────────────────────────────
    {
        "title": "Plataforma Elevadora Articulada Genie Z-45/25J",
        "description": (
            "Genie Z-45/25J articulada de 15.7 m de altura de trabajo. "
            "Capacidad de cesta 227 kg, pluma articulada con alcance horizontal 7.6 m. "
            "La mas vendida en Espana para mantenimiento de fachadas y cubiertas. "
            "Funcionamiento diesel/electrico en modo dual."
        ),
        "machinery_type": MachineryType.PLATAFORMA_ELEVADORA,
        "brand": "Genie",
        "model": "Z-45/25J",
        "year": 2022,
        "condition": MachineryCondition.EXCELENTE,
        "capacity": "227 kg / 15.7 m",
        "weight": 7620,
        "fuel_type": "Diesel/Electrico",
        "daily_rate": 130.0,
        "weekly_rate": 720.0,
        "monthly_rate": 2500.0,
        "deposit": 1200.0,
        "location_city": "Sevilla",
        "location_province": "Sevilla",
        "delivery_available": True,
        "delivery_cost": 80.0,
        "requires_license": True,
        "insurance_included": True,
    },
    {
        "title": "Plataforma Elevadora Tijera JLG 3394RT",
        "description": (
            "JLG 3394RT plataforma de tijera todo terreno, altura 11.7 m. "
            "Motor diesel Deutz, traccion 4x4 para trabajos en exterior. "
            "Capacidad de cesta 454 kg, extension de plataforma 1.2 m. "
            "Muy usada en mantenimiento industrial y obras de nave."
        ),
        "machinery_type": MachineryType.PLATAFORMA_ELEVADORA,
        "brand": "JLG",
        "model": "3394RT",
        "year": 2021,
        "condition": MachineryCondition.BUENO,
        "capacity": "454 kg / 11.7 m",
        "weight": 5580,
        "fuel_type": "Diesel",
        "daily_rate": 110.0,
        "weekly_rate": 600.0,
        "monthly_rate": 2100.0,
        "deposit": 1000.0,
        "location_city": "Bilbao",
        "location_province": "Vizcaya",
        "delivery_available": True,
        "delivery_cost": 70.0,
        "requires_license": True,
        "insurance_included": True,
    },

    # ── 11. Carretillas Elevadoras ────────────────────────────────────────────
    {
        "title": "Carretilla Elevadora Toyota 8FBN25",
        "description": (
            "Toyota 8FBN25 electrica de 2.5 t, la carretilla mas vendida en Europa. "
            "Motor electrico AC de 3 fases, bateria de 48V/930Ah. "
            "Optima para almacenes, obras de interior y carga de camiones. "
            "Sistema SAS (Sistema Activo de Estabilidad) de Toyota."
        ),
        "machinery_type": MachineryType.CARRETILLA_ELEVADORA,
        "brand": "Toyota",
        "model": "8FBN25",
        "year": 2022,
        "condition": MachineryCondition.EXCELENTE,
        "capacity": "2.5 t",
        "weight": 3700,
        "fuel_type": "Electrico",
        "daily_rate": 70.0,
        "weekly_rate": 380.0,
        "monthly_rate": 1300.0,
        "deposit": 500.0,
        "location_city": "Zaragoza",
        "location_province": "Zaragoza",
        "delivery_available": True,
        "delivery_cost": 60.0,
        "requires_operator": False,
        "requires_license": True,
        "insurance_included": False,
    },
    {
        "title": "Carretilla Elevadora Linde H25D",
        "description": (
            "Linde H25D diesel de 2.5 t, para exterior e interior. "
            "Motor Volkswagen diesel de 47 kW, transmision hidrostática. "
            "Muy utilizada en obras para descarga de palets de material. "
            "Sistema de proteccion de motor y transmision Linde Safety Pilot."
        ),
        "machinery_type": MachineryType.CARRETILLA_ELEVADORA,
        "brand": "Linde",
        "model": "H25D",
        "year": 2020,
        "condition": MachineryCondition.BUENO,
        "capacity": "2.5 t",
        "weight": 4200,
        "fuel_type": "Diesel",
        "daily_rate": 75.0,
        "weekly_rate": 400.0,
        "monthly_rate": 1400.0,
        "deposit": 500.0,
        "location_city": "Valladolid",
        "location_province": "Valladolid",
        "delivery_available": True,
        "delivery_cost": 65.0,
        "requires_operator": False,
        "requires_license": True,
        "insurance_included": False,
    },

    # ── 12. Compactadoras ─────────────────────────────────────────────────────
    {
        "title": "Compactadora Rodillo Bomag BW 213 D-5",
        "description": (
            "Bomag BW 213 D-5 rodillo vibratorio de 13 t para compactacion de tierra. "
            "Amplitud de vibracion 0.95/1.9 mm, fuerza centrifuga 260 kN. "
            "Sistema BOMAG Terrameter para medicion de la compactacion en tiempo real. "
            "El rodillo mas extendido en obras viales y terraplenes."
        ),
        "machinery_type": MachineryType.COMPACTADORA,
        "brand": "Bomag",
        "model": "BW 213 D-5",
        "year": 2021,
        "condition": MachineryCondition.EXCELENTE,
        "capacity": "13 t",
        "weight": 13000,
        "fuel_type": "Diesel",
        "daily_rate": 190.0,
        "weekly_rate": 1050.0,
        "monthly_rate": 3700.0,
        "deposit": 1800.0,
        "location_city": "Malaga",
        "location_province": "Malaga",
        "delivery_available": True,
        "delivery_cost": 140.0,
        "requires_operator": False,
        "insurance_included": False,
    },
    {
        "title": "Compactadora Dynapac CA6000D",
        "description": (
            "Dynapac CA6000D rodillo de 17 t para compactacion de asfalto y tierra. "
            "Tambor de 2.13 m de ancho, fuerza centrifuga de 352 kN. "
            "Sistema SEISMIC de medicion continua de compactacion. "
            "Alta productividad en bases de carretera y pavimentacion."
        ),
        "machinery_type": MachineryType.COMPACTADORA,
        "brand": "Dynapac",
        "model": "CA6000D",
        "year": 2020,
        "condition": MachineryCondition.BUENO,
        "capacity": "17 t",
        "weight": 17000,
        "fuel_type": "Diesel",
        "daily_rate": 220.0,
        "weekly_rate": 1250.0,
        "monthly_rate": 4400.0,
        "deposit": 2200.0,
        "location_city": "Burgos",
        "location_province": "Burgos",
        "delivery_available": True,
        "delivery_cost": 160.0,
        "requires_operator": False,
        "insurance_included": False,
    },

    # ── 13. Motoniveladora ────────────────────────────────────────────────────
    {
        "title": "Motoniveladora Caterpillar 140M3",
        "description": (
            "CAT 140M3 con motor Cat C7.1 de 138 kW. "
            "Hoja motoniveladora de 3.7 m, profundidad de corte 610 mm. "
            "Sistema Cat AccuGrade listo para conectar GPS. "
            "Imprescindible para perfilado de carreteras, explanaciones y bases de vial."
        ),
        "machinery_type": MachineryType.MOTONIVELADORA,
        "brand": "Caterpillar",
        "model": "140M3",
        "year": 2020,
        "condition": MachineryCondition.BUENO,
        "capacity": "3.7 m hoja",
        "weight": 17000,
        "fuel_type": "Diesel",
        "daily_rate": 380.0,
        "weekly_rate": 2200.0,
        "monthly_rate": 7800.0,
        "deposit": 3500.0,
        "location_city": "Zaragoza",
        "location_province": "Zaragoza",
        "delivery_available": True,
        "delivery_cost": 250.0,
        "requires_operator": True,
        "insurance_included": False,
    },

    # ── 14. Martillo Hidraulico ───────────────────────────────────────────────
    {
        "title": "Martillo Hidraulico Epiroc HB 3100",
        "description": (
            "Epiroc HB 3100 de 3100 kg para excavadoras de 30-70 t. "
            "Energia de golpe 12000 J, frecuencia 300-450 rpm. "
            "AutoControl y PowerAdapt para adaptacion automatica. "
            "El mas potente de su clase para demolicion de hormigon armado."
        ),
        "machinery_type": MachineryType.MARTILLO_HIDRAULICO,
        "brand": "Epiroc",
        "model": "HB 3100",
        "year": 2021,
        "condition": MachineryCondition.BUENO,
        "capacity": "3100 kg / 12000 J",
        "weight": 3100,
        "daily_rate": 150.0,
        "weekly_rate": 850.0,
        "monthly_rate": 3000.0,
        "deposit": 2000.0,
        "location_city": "Madrid",
        "location_province": "Madrid",
        "delivery_available": True,
        "delivery_cost": 80.0,
        "requires_operator": False,
        "insurance_included": False,
    },
    {
        "title": "Martillo Hidraulico Atlas Copco HB 4100",
        "description": (
            "Atlas Copco HB 4100 de 4100 kg para equipos portadores de 36-75 t. "
            "Sistema VibroSilenced XP para reduccion de vibraciones al operador. "
            "ContiLube II para lubricacion automatica continua. "
            "Ideal para demolicion de estructuras y trabajo en mineria."
        ),
        "machinery_type": MachineryType.MARTILLO_HIDRAULICO,
        "brand": "Atlas Copco",
        "model": "HB 4100",
        "year": 2020,
        "condition": MachineryCondition.BUENO,
        "capacity": "4100 kg",
        "weight": 4100,
        "daily_rate": 170.0,
        "weekly_rate": 950.0,
        "monthly_rate": 3300.0,
        "deposit": 2000.0,
        "location_city": "Bilbao",
        "location_province": "Vizcaya",
        "delivery_available": True,
        "delivery_cost": 100.0,
        "requires_operator": False,
        "insurance_included": False,
    },

    # ── 15. Compresor ─────────────────────────────────────────────────────────
    {
        "title": "Compresor de Aire Atlas Copco XATS 138",
        "description": (
            "Atlas Copco XATS 138 Kd, compresor de tornillo movil de 138 HP. "
            "Caudal libre 8.0 m3/min a 7 bar. "
            "Motor Kubota diesel de 4 cilindros. "
            "El compresor movil mas utilizado en obras civiles y mineria en Espana."
        ),
        "machinery_type": MachineryType.COMPRESOR,
        "brand": "Atlas Copco",
        "model": "XATS 138 Kd",
        "year": 2021,
        "condition": MachineryCondition.EXCELENTE,
        "capacity": "8.0 m3/min a 7 bar",
        "weight": 1560,
        "fuel_type": "Diesel",
        "daily_rate": 85.0,
        "weekly_rate": 470.0,
        "monthly_rate": 1650.0,
        "deposit": 600.0,
        "location_city": "Alicante",
        "location_province": "Alicante",
        "delivery_available": True,
        "delivery_cost": 50.0,
        "requires_operator": False,
        "insurance_included": False,
    },

    # ── 16. Generador ─────────────────────────────────────────────────────────
    {
        "title": "Generador Himoinsa HHW-35 T5",
        "description": (
            "Himoinsa HHW-35 T5 de 35 kVA con motor Hatz diesel. "
            "Ideal para obras en zonas sin suministro electrico. "
            "Sistema AVR para tension estable, cuadro ATS incluido. "
            "El grupo electrogeno mas vendido para obra en Espana."
        ),
        "machinery_type": MachineryType.GENERADOR,
        "brand": "Himoinsa",
        "model": "HHW-35 T5",
        "year": 2022,
        "condition": MachineryCondition.EXCELENTE,
        "capacity": "35 kVA",
        "weight": 620,
        "fuel_type": "Diesel",
        "daily_rate": 55.0,
        "weekly_rate": 300.0,
        "monthly_rate": 1050.0,
        "deposit": 300.0,
        "location_city": "Sevilla",
        "location_province": "Sevilla",
        "delivery_available": True,
        "delivery_cost": 40.0,
        "requires_operator": False,
        "insurance_included": False,
    },
    {
        "title": "Generador Aggreko 100 kVA Stage V",
        "description": (
            "Aggreko 100 kVA Stage V con motor John Deere Stage 5. "
            "Grupo electrogeno de alta potencia para obras con gran consumo. "
            "Nivel sonoro reducido 67 dB(A) a 7 m. "
            "Sistema telemetria remota para monitorizacion 24h."
        ),
        "machinery_type": MachineryType.GENERADOR,
        "brand": "Aggreko",
        "model": "100 kVA Stage V",
        "year": 2022,
        "condition": MachineryCondition.EXCELENTE,
        "capacity": "100 kVA",
        "weight": 1450,
        "fuel_type": "Diesel",
        "daily_rate": 110.0,
        "weekly_rate": 620.0,
        "monthly_rate": 2200.0,
        "deposit": 600.0,
        "location_city": "Madrid",
        "location_province": "Madrid",
        "delivery_available": True,
        "delivery_cost": 70.0,
        "requires_operator": False,
        "insurance_included": False,
    },

    # ── 17. Montacargas ───────────────────────────────────────────────────────
    {
        "title": "Montacargas de Obra Genie GS-3390",
        "description": (
            "Genie GS-3390 RT tijera todo terreno con altura de trabajo 11.7 m. "
            "Motor diesel, traccion 4x4, plataforma de 3.68 x 1.83 m. "
            "Muy utilizado en obras de naves y edificacion para subida de materiales. "
            "Puede operar en pendientes de hasta 40%."
        ),
        "machinery_type": MachineryType.MONTACARGAS,
        "brand": "Genie",
        "model": "GS-3390 RT",
        "year": 2021,
        "condition": MachineryCondition.BUENO,
        "capacity": "680 kg / 11.7 m",
        "weight": 5200,
        "fuel_type": "Diesel",
        "daily_rate": 95.0,
        "weekly_rate": 530.0,
        "monthly_rate": 1850.0,
        "deposit": 700.0,
        "location_city": "Alicante",
        "location_province": "Alicante",
        "delivery_available": True,
        "delivery_cost": 60.0,
        "requires_operator": False,
        "requires_license": True,
        "insurance_included": False,
    },

    # ── 18. Bomba de Hormigon ─────────────────────────────────────────────────
    {
        "title": "Bomba de Hormigon Putzmeister BSF 36Z.16H",
        "description": (
            "Putzmeister BSF 36Z con pluma plegable de 36 m de alcance vertical. "
            "Presion de hormigonado de 85 bar, caudal maximo 90 m3/h. "
            "La bomba de brazo mas usada en edificacion residencial en Espana. "
            "Control remoto por radio para mayor seguridad del operario."
        ),
        "machinery_type": MachineryType.BOMBA_HORMIGON,
        "brand": "Putzmeister",
        "model": "BSF 36Z.16H",
        "year": 2020,
        "condition": MachineryCondition.BUENO,
        "capacity": "90 m3/h / 36 m pluma",
        "fuel_type": "Diesel",
        "daily_rate": 500.0,
        "weekly_rate": 2900.0,
        "monthly_rate": 10000.0,
        "deposit": 5000.0,
        "location_city": "Madrid",
        "location_province": "Madrid",
        "delivery_available": False,
        "requires_operator": True,
        "requires_license": True,
        "insurance_included": True,
    },
    {
        "title": "Bomba de Hormigon Schwing S 36 SX",
        "description": (
            "Schwing S 36 SX con pluma de 36.2 m, radio de despliegue 32.9 m. "
            "Caudal maximo 130 m3/h con bomba de doble piston. "
            "Sistema EBC (Electronic Boom Control) para manejo preciso. "
            "Muy extendida en losas de gran superficie y tuneles."
        ),
        "machinery_type": MachineryType.BOMBA_HORMIGON,
        "brand": "Schwing",
        "model": "S 36 SX",
        "year": 2021,
        "condition": MachineryCondition.BUENO,
        "capacity": "130 m3/h / 36 m pluma",
        "fuel_type": "Diesel",
        "daily_rate": 520.0,
        "weekly_rate": 3000.0,
        "monthly_rate": 10500.0,
        "deposit": 5000.0,
        "location_city": "Barcelona",
        "location_province": "Barcelona",
        "delivery_available": False,
        "requires_operator": True,
        "requires_license": True,
        "insurance_included": True,
    },

    # ── 19. Cortadora de Asfalto ──────────────────────────────────────────────
    {
        "title": "Cortadora de Asfalto Husqvarna FS 7000 D",
        "description": (
            "Husqvarna FS 7000 D cortadora de pavimento con motor diesel Hatz. "
            "Profundidad de corte 410 mm con disco de 900 mm. "
            "Sistema de guia laser para cortes rectos en calzada. "
            "La mas usada por empresas de servicios publicos en Espana para reparacion de viales."
        ),
        "machinery_type": MachineryType.CORTADORA_ASFALTO,
        "brand": "Husqvarna",
        "model": "FS 7000 D",
        "year": 2022,
        "condition": MachineryCondition.EXCELENTE,
        "capacity": "410 mm profundidad",
        "weight": 420,
        "fuel_type": "Diesel",
        "daily_rate": 60.0,
        "weekly_rate": 330.0,
        "monthly_rate": 1150.0,
        "deposit": 400.0,
        "location_city": "Valencia",
        "location_province": "Valencia",
        "delivery_available": True,
        "delivery_cost": 35.0,
        "requires_operator": False,
        "insurance_included": False,
    },

    # ── 20. Andamio ───────────────────────────────────────────────────────────
    {
        "title": "Andamio Modular Layher Allround",
        "description": (
            "Sistema de andamiaje modular Layher Allround para fachadas y rehabilitacion. "
            "Roseta con 8 aperturas para conexiones en cualquier angulo. "
            "Capacidad de carga 3 kN/m2. "
            "El sistema de andamiaje mas vendido en Europa, usado en edificios singulares."
        ),
        "machinery_type": MachineryType.ANDAMIO,
        "brand": "Layher",
        "model": "Allround",
        "year": 2020,
        "condition": MachineryCondition.BUENO,
        "capacity": "3 kN/m2",
        "daily_rate": 2.5,
        "weekly_rate": 12.0,
        "monthly_rate": 40.0,
        "deposit": 500.0,
        "location_city": "Madrid",
        "location_province": "Madrid",
        "delivery_available": True,
        "delivery_cost": 200.0,
        "requires_operator": False,
        "insurance_included": False,
    },
]


# ── Funcion principal de seed ──────────────────────────────────────────────────

def run():
    db = SessionLocal()
    try:
        # 1. Obtener o crear usuario catalogo
        user = db.query(User).filter(User.email == CATALOG_USER["email"]).first()
        if not user:
            user = User(**CATALOG_USER)
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"Usuario catalogo creado: {user.email}")
        else:
            print(f"Usuario catalogo ya existe: {user.email}")

        # 2. Insertar cada maquina si no existe ya (por titulo)
        inserted = 0
        skipped = 0
        for data in MACHINERY_SEED:
            exists = db.query(Machinery).filter(Machinery.title == data["title"]).first()
            if exists:
                skipped += 1
                continue
            m = Machinery(**data, owner_id=user.id, is_available=True, is_active=True)
            db.add(m)
            inserted += 1

        db.commit()
        print(f"\n{inserted} maquinas insertadas, {skipped} ya existian.")
        print("Seed completado correctamente.")

    except Exception as e:
        db.rollback()
        print(f"ERROR: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run()
