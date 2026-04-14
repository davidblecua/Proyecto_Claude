"""
Seed: 15 jefes de obra (consumer) + 30 peticiones de maquinaria

Uso:
    cd 01_codigo/backend
    APP_ENV=test python -m seeds.seed_machinery_requests

Es idempotente: comprueba por email antes de insertar usuarios,
y por (user_id + machinery_type + city + start_date) para las peticiones.
"""
import sys
import os
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal
from app.models.user import User, UserRole
from app.models.machinery import MachineryType
from app.models.machinery_request import MachineryRequest, RequestStatus
from app.models import machinery as _m   # noqa: registrar tablas en metadata
from app.models import booking as _b     # noqa
from app.models import message as _msg   # noqa
from app.models import operator as _op   # noqa
from app.core.security import get_password_hash

NOW = datetime.now(timezone.utc)


def d(days_start: int, days_end: int):
    """Devuelve (start_date, end_date) como datetimes UTC a partir de hoy."""
    return (
        NOW + timedelta(days=days_start),
        NOW + timedelta(days=days_end),
    )


# ── 15 jefes de obra ─────────────────────────────────────────────────────────

CONSUMERS = [
    {
        "email": "ana.garcia@constructoraoliva.com",
        "username": "ana_garcia_oliva",
        "full_name": "Ana García Molina",
        "company_name": "Constructora Oliva S.L.",
        "phone": "612 111 001",
    },
    {
        "email": "carlos.medina@obrasmedina.es",
        "username": "carlos_medina_obras",
        "full_name": "Carlos Medina Herrero",
        "company_name": "Obras Medina e Hijos S.A.",
        "phone": "623 111 002",
    },
    {
        "email": "laura.fontana@grupofontana.com",
        "username": "laura_fontana",
        "full_name": "Laura Fontana Ruiz",
        "company_name": "Grupo Fontana Construcciones",
        "phone": "634 111 003",
    },
    {
        "email": "javier.roca@edificacionesroca.es",
        "username": "javier_roca_edif",
        "full_name": "Javier Roca Sánchez",
        "company_name": "Edificaciones Roca S.L.",
        "phone": "645 111 004",
    },
    {
        "email": "maria.mateo@construmateo.com",
        "username": "maria_mateo_const",
        "full_name": "María Mateo Pérez",
        "company_name": "Construmateo S.A.",
        "phone": "656 111 005",
    },
    {
        "email": "pedro.oliva@constructoraoliva.com",
        "username": "pedro_oliva_zar",
        "full_name": "Pedro Oliva Torres",
        "company_name": "Constructora Oliva S.L.",
        "phone": "667 111 006",
    },
    {
        "email": "isabel.guerrero@obrasmedina.es",
        "username": "isabel_guerrero",
        "full_name": "Isabel Guerrero Castro",
        "company_name": "Obras Medina e Hijos S.A.",
        "phone": "678 111 007",
    },
    {
        "email": "rafael.blanco@grupofontana.com",
        "username": "rafael_blanco_mur",
        "full_name": "Rafael Blanco Moreno",
        "company_name": "Grupo Fontana Construcciones",
        "phone": "689 111 008",
    },
    {
        "email": "carmen.delgado@edificacionesroca.es",
        "username": "carmen_delgado",
        "full_name": "Carmen Delgado Ortiz",
        "company_name": "Edificaciones Roca S.L.",
        "phone": "690 111 009",
    },
    {
        "email": "alberto.navarro@construmateo.com",
        "username": "alberto_navarro",
        "full_name": "Alberto Navarro Gil",
        "company_name": "Construmateo S.A.",
        "phone": "601 111 010",
    },
    {
        "email": "sofia.montero@obrascordova.es",
        "username": "sofia_montero_cor",
        "full_name": "Sofía Montero Vega",
        "company_name": "Obras Córdoba S.L.",
        "phone": "612 222 011",
    },
    {
        "email": "diego.serrano@constructoraoliva.com",
        "username": "diego_serrano_pal",
        "full_name": "Diego Serrano Leal",
        "company_name": "Constructora Oliva S.L.",
        "phone": "623 222 012",
    },
    {
        "email": "elena.prada@gruposilvestre.com",
        "username": "elena_prada_lpa",
        "full_name": "Elena Prada Fuentes",
        "company_name": "Grupo Silvestre S.A.",
        "phone": "634 222 013",
    },
    {
        "email": "marcos.ibanez@obrasnorte.es",
        "username": "marcos_ibanez_san",
        "full_name": "Marcos Ibáñez Rodríguez",
        "company_name": "Obras Norte S.L.",
        "phone": "645 222 014",
    },
    {
        "email": "lucia.campos@construgranada.es",
        "username": "lucia_campos_gra",
        "full_name": "Lucía Campos Reyes",
        "company_name": "Construgranada S.A.",
        "phone": "656 222 015",
    },
]

# Contraseña única para todos los usuarios de prueba
_PASSWORD_HASH = get_password_hash("JefeObra2024!")


# ── Peticiones: (email_usuario, datos_peticion) ───────────────────────────────
# 30 peticiones totales: 22 open (73%), 8 closed (27%)

REQUESTS_DATA = [
    # ── Ana García — 3 peticiones ────────────────────────────────────────────
    {
        "user_email": "ana.garcia@constructoraoliva.com",
        "machinery_type": MachineryType.EXCAVADORA,
        "city": "Barcelona",
        "province": "Barcelona",
        "start_date_offset": 14,
        "end_date_offset": 28,
        "budget_per_day": 480.0,
        "status": RequestStatus.OPEN,
        "description": (
            "Necesitamos excavadora de cadenas para movimiento de tierras en urbanización "
            "de 45 viviendas en Vallès Occidental. Terreno arcilloso con nivel freático alto. "
            "Acceso por camino secundario de 4m de ancho."
        ),
    },
    {
        "user_email": "ana.garcia@constructoraoliva.com",
        "machinery_type": MachineryType.GRUA_TORRE,
        "city": "Barcelona",
        "province": "Barcelona",
        "start_date_offset": 30,
        "end_date_offset": 72,
        "budget_per_day": 550.0,
        "status": RequestStatus.CLOSED,
        "description": (
            "Construcción de edificio residencial de 12 plantas en el Eixample. "
            "Precisamos grúa torre con alcance mínimo 45m y capacidad 8t en punta. "
            "Obra en zona urbana densa, montaje nocturno."
        ),
    },
    {
        "user_email": "ana.garcia@constructoraoliva.com",
        "machinery_type": MachineryType.COMPACTADORA,
        "city": "Barcelona",
        "province": "Barcelona",
        "start_date_offset": 21,
        "end_date_offset": 31,
        "budget_per_day": 280.0,
        "status": RequestStatus.OPEN,
        "description": (
            "Compactadora de rodillo para base de solera industrial en nave logística 3.800m². "
            "Material granular aportado, se requieren 3 pasadas de compactación a Proctor 98%."
        ),
    },

    # ── Carlos Medina — 3 peticiones ─────────────────────────────────────────
    {
        "user_email": "carlos.medina@obrasmedina.es",
        "machinery_type": MachineryType.RETROEXCAVADORA,
        "city": "Madrid",
        "province": "Madrid",
        "start_date_offset": 10,
        "end_date_offset": 24,
        "budget_per_day": 390.0,
        "status": RequestStatus.OPEN,
        "description": (
            "Retroexcavadora para apertura de zanjas de saneamiento en urbanización residencial. "
            "Profundidad media 2,5m. Terreno con presencia de roca blanda en el último metro. "
            "Se valorará equipo con martillo hidráulico incluido."
        ),
    },
    {
        "user_email": "carlos.medina@obrasmedina.es",
        "machinery_type": MachineryType.PLATAFORMA_ELEVADORA,
        "city": "Madrid",
        "province": "Madrid",
        "start_date_offset": 18,
        "end_date_offset": 32,
        "budget_per_day": 310.0,
        "status": RequestStatus.OPEN,
        "description": (
            "Rehabilitación de fachada en edificio de 9 plantas en el barrio de Salamanca. "
            "Necesitamos plataforma articulada con alcance mínimo 30m. "
            "Trabajo en fachada con restricciones de espacio público, permiso municipal gestionado."
        ),
    },
    {
        "user_email": "carlos.medina@obrasmedina.es",
        "machinery_type": MachineryType.BOMBA_HORMIGON,
        "city": "Madrid",
        "province": "Madrid",
        "start_date_offset": 45,
        "end_date_offset": 67,
        "budget_per_day": None,
        "status": RequestStatus.CLOSED,
        "description": (
            "Bomba estacionaria de hormigón para losas de forjado en obra de 6 plantas. "
            "Estimamos 4 bombeos de 80m³ cada uno. Acceso restringido por calle estrecha, "
            "se necesita bomba con brazo de al menos 36m."
        ),
    },

    # ── Laura Fontana — 3 peticiones ─────────────────────────────────────────
    {
        "user_email": "laura.fontana@grupofontana.com",
        "machinery_type": MachineryType.DUMPER,
        "city": "Valencia",
        "province": "Valencia",
        "start_date_offset": 16,
        "end_date_offset": 37,
        "budget_per_day": 220.0,
        "status": RequestStatus.OPEN,
        "description": (
            "Dumper articulado de 25t para transporte interior de tierras en obras de "
            "infraestructura viaria. Pista de obra habilitada de 1,2km. "
            "Estimamos 3 semanas de trabajo continuo."
        ),
    },
    {
        "user_email": "laura.fontana@grupofontana.com",
        "machinery_type": MachineryType.HORMIGONERA,
        "city": "Valencia",
        "province": "Valencia",
        "start_date_offset": 25,
        "end_date_offset": 46,
        "budget_per_day": 145.0,
        "status": RequestStatus.CLOSED,
        "description": (
            "Hormigonera de obra de 500L para trabajos de rehabilitación en cuatro viviendas "
            "unifamiliares. Producción estimada 3-4m³/día. Se requiere transporte incluido."
        ),
    },
    {
        "user_email": "laura.fontana@grupofontana.com",
        "machinery_type": MachineryType.MANIPULADOR_TELESCOPICO,
        "city": "Valencia",
        "province": "Valencia",
        "start_date_offset": 35,
        "end_date_offset": 56,
        "budget_per_day": 330.0,
        "status": RequestStatus.OPEN,
        "description": (
            "Manipulador telescópico para colocación de estructura prefabricada en nave industrial 4.500m². "
            "Altura máxima requerida 14m, carga punta 4t. Terreno con pendiente moderada, "
            "tracción en las 4 ruedas imprescindible."
        ),
    },

    # ── Javier Roca — 3 peticiones ───────────────────────────────────────────
    {
        "user_email": "javier.roca@edificacionesroca.es",
        "machinery_type": MachineryType.EXCAVADORA,
        "city": "Sevilla",
        "province": "Sevilla",
        "start_date_offset": 12,
        "end_date_offset": 26,
        "budget_per_day": 460.0,
        "status": RequestStatus.OPEN,
        "description": (
            "Excavadora hidráulica de gran tonelaje para vaciado de sótano en edificio "
            "plurifamiliar de 18 viviendas. Profundidad -4,5m, superficie 850m². "
            "Entorno urbano con edificios colindantes, apuntalamiento previo ejecutado."
        ),
    },
    {
        "user_email": "javier.roca@edificacionesroca.es",
        "machinery_type": MachineryType.CAMION_GRUA,
        "city": "Sevilla",
        "province": "Sevilla",
        "start_date_offset": 28,
        "end_date_offset": 42,
        "budget_per_day": 520.0,
        "status": RequestStatus.OPEN,
        "description": (
            "Camión grúa telescópica de 60t para izado de vigas prefabricadas de hormigón "
            "en polideportivo municipal. Peso máximo por pieza 18t, altura de trabajo 12m. "
            "Zona de trabajo accesible para vehículo pesado."
        ),
    },
    {
        "user_email": "javier.roca@edificacionesroca.es",
        "machinery_type": MachineryType.PALA_CARGADORA,
        "city": "Sevilla",
        "province": "Sevilla",
        "start_date_offset": 55,
        "end_date_offset": 76,
        "budget_per_day": None,
        "status": RequestStatus.CLOSED,
        "description": (
            "Pala cargadora para gestión de áridos en planta de tratamiento de residuos de "
            "construcción. Jornada de 8h/día, 5 días/semana. Cuchara de 2,5m³ mínimo."
        ),
    },

    # ── María Mateo — 3 peticiones ───────────────────────────────────────────
    {
        "user_email": "maria.mateo@construmateo.com",
        "machinery_type": MachineryType.GRUA_TORRE,
        "city": "Bilbao",
        "province": "Vizcaya",
        "start_date_offset": 20,
        "end_date_offset": 62,
        "budget_per_day": 580.0,
        "status": RequestStatus.OPEN,
        "description": (
            "Grúa torre para construcción de complejo residencial de 3 bloques de 8 plantas. "
            "Radio de trabajo 50m, capacidad mínima 10t en punta. "
            "Parcela de 2.800m², terreno con relleno antrópico, cimentación con micropilotes."
        ),
    },
    {
        "user_email": "maria.mateo@construmateo.com",
        "machinery_type": MachineryType.CARRETILLA_ELEVADORA,
        "city": "Bilbao",
        "province": "Vizcaya",
        "start_date_offset": 15,
        "end_date_offset": 29,
        "budget_per_day": 160.0,
        "status": RequestStatus.OPEN,
        "description": (
            "Carretilla elevadora todoterreno para descarga y distribución de materiales en "
            "obra de rehabilitación integral de nave industrial. Mástil libre de 4,5m, "
            "capacidad 3,5t. Suelo irregular de hormigón en mal estado."
        ),
    },
    {
        "user_email": "maria.mateo@construmateo.com",
        "machinery_type": MachineryType.MOTONIVELADORA,
        "city": "Bilbao",
        "province": "Vizcaya",
        "start_date_offset": 40,
        "end_date_offset": 54,
        "budget_per_day": None,
        "status": RequestStatus.CLOSED,
        "description": (
            "Motoniveladora para conformación de explanada en acceso a polígono industrial. "
            "Longitud 380m, anchura 12m. Material suelto con clasificación media. "
            "Se requiere rasante con pendiente longitudinal del 2% y transversal 3%."
        ),
    },

    # ── Pedro Oliva — 2 peticiones ───────────────────────────────────────────
    {
        "user_email": "pedro.oliva@constructoraoliva.com",
        "machinery_type": MachineryType.EXCAVADORA,
        "city": "Zaragoza",
        "province": "Zaragoza",
        "start_date_offset": 17,
        "end_date_offset": 31,
        "budget_per_day": 440.0,
        "status": RequestStatus.OPEN,
        "description": (
            "Excavadora de cadenas para demolición de edificio antiguo de 3 plantas y "
            "posterior retirada de escombros. Solar urbano de 320m², paredes medianeras en buen estado. "
            "Se requiere equipo con pulpo hidráulico."
        ),
    },
    {
        "user_email": "pedro.oliva@constructoraoliva.com",
        "machinery_type": MachineryType.COMPACTADORA,
        "city": "Zaragoza",
        "province": "Zaragoza",
        "start_date_offset": 33,
        "end_date_offset": 47,
        "budget_per_day": 260.0,
        "status": RequestStatus.OPEN,
        "description": (
            "Compactadora de bandas para terraplén de acceso a nueva zona industrial. "
            "Volumen aproximado 8.500m³ de terraplén. Material procedente de préstamos, "
            "clasificado como tolerable. Control de compactación in situ."
        ),
    },

    # ── Isabel Guerrero — 2 peticiones ──────────────────────────────────────
    {
        "user_email": "isabel.guerrero@obrasmedina.es",
        "machinery_type": MachineryType.PLATAFORMA_ELEVADORA,
        "city": "Málaga",
        "province": "Málaga",
        "start_date_offset": 19,
        "end_date_offset": 33,
        "budget_per_day": 295.0,
        "status": RequestStatus.OPEN,
        "description": (
            "Plataforma elevadora de tijera para trabajos de pintura y reparación de cubierta "
            "en nave logística de 6.000m². Altura máxima 14m, plataforma de al menos 8m² de trabajo. "
            "Suelo de hormigón interior, carga de pavimento 15 kN/m²."
        ),
    },
    {
        "user_email": "isabel.guerrero@obrasmedina.es",
        "machinery_type": MachineryType.BULLDOZER,
        "city": "Málaga",
        "province": "Málaga",
        "start_date_offset": 50,
        "end_date_offset": 71,
        "budget_per_day": None,
        "status": RequestStatus.CLOSED,
        "description": (
            "Bulldozer D6 o equivalente para desbroce y limpieza de parcela de 12 hectáreas "
            "en zona periurbana. Vegetación arbustiva densa con algunos árboles. "
            "Material resultante a verter en zona de préstamos a 500m."
        ),
    },

    # ── Rafael Blanco — 2 peticiones ─────────────────────────────────────────
    {
        "user_email": "rafael.blanco@grupofontana.com",
        "machinery_type": MachineryType.BOMBA_HORMIGON,
        "city": "Murcia",
        "province": "Murcia",
        "start_date_offset": 22,
        "end_date_offset": 44,
        "budget_per_day": 380.0,
        "status": RequestStatus.OPEN,
        "description": (
            "Bomba pluma autopropulsada para hormigonado de muros de contención en sótano "
            "de aparcamiento subterráneo de 4 plantas. Distancia de bombeo hasta 40m, "
            "altura de trabajo -14m. Producción media 60m³/jornada."
        ),
    },
    {
        "user_email": "rafael.blanco@grupofontana.com",
        "machinery_type": MachineryType.RETROEXCAVADORA,
        "city": "Murcia",
        "province": "Murcia",
        "start_date_offset": 48,
        "end_date_offset": 62,
        "budget_per_day": 350.0,
        "status": RequestStatus.OPEN,
        "description": (
            "Retroexcavadora mixta para trabajos de urbanización: pavimentación de aceras, "
            "instalación de bordillos y reparación de calzada. Obra lineal de 620m en calle urbana, "
            "tráfico cortado parcialmente."
        ),
    },

    # ── Carmen Delgado — 2 peticiones ────────────────────────────────────────
    {
        "user_email": "carmen.delgado@edificacionesroca.es",
        "machinery_type": MachineryType.GRUA_TORRE,
        "city": "Alicante",
        "province": "Alicante",
        "start_date_offset": 26,
        "end_date_offset": 68,
        "budget_per_day": 560.0,
        "status": RequestStatus.OPEN,
        "description": (
            "Grúa torre para construcción de hotel de 14 plantas junto al paseo marítimo. "
            "Giro sobre terreno con viento frecuente superior a 60 km/h. "
            "Se requiere grúa con anemómetro y parada automática certificada."
        ),
    },
    {
        "user_email": "carmen.delgado@edificacionesroca.es",
        "machinery_type": MachineryType.DUMPER,
        "city": "Alicante",
        "province": "Alicante",
        "start_date_offset": 14,
        "end_date_offset": 28,
        "budget_per_day": 195.0,
        "status": RequestStatus.CLOSED,
        "description": (
            "Dumper de obra de 6t para transporte interior de escombros en demolición de "
            "hotel antiguo de 8 plantas. Rampa de salida del 18%, suelo adoquinado. "
            "Jornada intensiva de 10h diarias, 4 semanas."
        ),
    },

    # ── Alberto Navarro — 2 peticiones ───────────────────────────────────────
    {
        "user_email": "alberto.navarro@construmateo.com",
        "machinery_type": MachineryType.PALA_CARGADORA,
        "city": "Valladolid",
        "province": "Valladolid",
        "start_date_offset": 23,
        "end_date_offset": 37,
        "budget_per_day": 270.0,
        "status": RequestStatus.OPEN,
        "description": (
            "Pala cargadora de ruedas para carga y transporte de áridos en obra de "
            "construcción de 80 viviendas unifamiliares. Campa de acopio de 2.000m², "
            "ciclos cortos de carga. 8h/día, 6 días/semana."
        ),
    },
    {
        "user_email": "alberto.navarro@construmateo.com",
        "machinery_type": MachineryType.HORMIGONERA,
        "city": "Valladolid",
        "province": "Valladolid",
        "start_date_offset": 38,
        "end_date_offset": 52,
        "budget_per_day": 130.0,
        "status": RequestStatus.OPEN,
        "description": (
            "Dos hormigoneras de 350L para trabajos de solados y alicatados en promoción de "
            "viviendas. Se necesita transporte a obra y recogida al terminar el alquiler. "
            "Disponibilidad inmediata, entrega en 48h."
        ),
    },

    # ── Sofía Montero — 1 petición ───────────────────────────────────────────
    {
        "user_email": "sofia.montero@obrascordova.es",
        "machinery_type": MachineryType.EXCAVADORA,
        "city": "Córdoba",
        "province": "Córdoba",
        "start_date_offset": 29,
        "end_date_offset": 50,
        "budget_per_day": 420.0,
        "status": RequestStatus.OPEN,
        "description": (
            "Excavadora de cadenas para explanación y vaciado en promoción de 28 viviendas "
            "adosadas en zona residencial de nueva creación. Volumen de excavación 14.000m³, "
            "terreno con arcillas expansivas, nivel freático a -3m."
        ),
    },

    # ── Diego Serrano — 1 petición ───────────────────────────────────────────
    {
        "user_email": "diego.serrano@constructoraoliva.com",
        "machinery_type": MachineryType.PLATAFORMA_ELEVADORA,
        "city": "Palma",
        "province": "Baleares",
        "start_date_offset": 24,
        "end_date_offset": 38,
        "budget_per_day": 320.0,
        "status": RequestStatus.OPEN,
        "description": (
            "Plataforma articulada autopropulsada para sustitución de instalación de climatización "
            "en cubierta de centro comercial. Altura de trabajo 22m, superficie de plataforma mínima 6m². "
            "Trabajo nocturno (22h-6h) para no interferir con actividad del centro."
        ),
    },

    # ── Elena Prada — 1 petición ─────────────────────────────────────────────
    {
        "user_email": "elena.prada@gruposilvestre.com",
        "machinery_type": MachineryType.CAMION_GRUA,
        "city": "Las Palmas",
        "province": "Las Palmas",
        "start_date_offset": 31,
        "end_date_offset": 45,
        "budget_per_day": 490.0,
        "status": RequestStatus.OPEN,
        "description": (
            "Camión grúa para izado e instalación de estructura metálica en cubierta de "
            "nave industrial 1.800m². Piezas de hasta 12t y 18m de longitud. "
            "Acceso por zona portuaria, restricciones horarias 8h-20h."
        ),
    },

    # ── Marcos Ibáñez — 1 petición ───────────────────────────────────────────
    {
        "user_email": "marcos.ibanez@obrasnorte.es",
        "machinery_type": MachineryType.COMPACTADORA,
        "city": "Santander",
        "province": "Cantabria",
        "start_date_offset": 42,
        "end_date_offset": 56,
        "budget_per_day": 240.0,
        "status": RequestStatus.CLOSED,
        "description": (
            "Compactadora de asfalto de doble rodillo para repavimentación de vial urbano de 850m. "
            "Mezcla bituminosa AC 16 surf 50/70 S, capa de rodadura de 5cm. "
            "Trabajo en turno nocturno, coordinación con empresa asfaltadora."
        ),
    },

    # ── Lucía Campos — 1 petición ────────────────────────────────────────────
    {
        "user_email": "lucia.campos@construgranada.es",
        "machinery_type": MachineryType.RETROEXCAVADORA,
        "city": "Granada",
        "province": "Granada",
        "start_date_offset": 27,
        "end_date_offset": 48,
        "budget_per_day": 370.0,
        "status": RequestStatus.OPEN,
        "description": (
            "Retroexcavadora para apertura de cimentación en edificio de 6 plantas en el "
            "Albaicín. Zona de casco histórico con restricciones arqueológicas. "
            "Se requiere equipo de pequeño tonelaje (hasta 8t) y brazo extendido de 5m mínimo."
        ),
    },
]


def run():
    db = SessionLocal()
    try:
        # ── 1. Crear / reutilizar usuarios ────────────────────────────────────
        print("\nCreando usuarios...")
        user_map: dict[str, int] = {}  # email -> id
        usuarios_creados = 0
        usuarios_existentes = 0

        for data in CONSUMERS:
            existing = db.query(User).filter(User.email == data["email"]).first()
            if existing:
                user_map[data["email"]] = existing.id
                usuarios_existentes += 1
                print(f"  — Ya existe: {data['email']}")
                continue

            user = User(
                email=data["email"],
                username=data["username"],
                hashed_password=_PASSWORD_HASH,
                full_name=data["full_name"],
                company_name=data["company_name"],
                phone=data["phone"],
                role=UserRole.CONSUMER,
                is_active=True,
                is_verified=True,
            )
            db.add(user)
            db.flush()
            user_map[data["email"]] = user.id
            usuarios_creados += 1
            print(f"  Creado: {data['email']}")

        db.commit()

        # ── 2. Crear peticiones (idempotente por user+tipo+ciudad+start_date) ─
        print("\nCreando peticiones de maquinaria...")
        peticiones_creadas = 0
        peticiones_existentes = 0
        open_count = 0
        closed_count = 0

        for req in REQUESTS_DATA:
            user_id = user_map[req["user_email"]]
            start, end = d(req["start_date_offset"], req["end_date_offset"])

            existing = (
                db.query(MachineryRequest)
                .filter(
                    MachineryRequest.user_id == user_id,
                    MachineryRequest.machinery_type == req["machinery_type"],
                    MachineryRequest.city == req["city"],
                )
                .first()
            )
            if existing:
                peticiones_existentes += 1
                print(f"  — Ya existe: {req['machinery_type'].value} en {req['city']}")
                continue

            new_req = MachineryRequest(
                user_id=user_id,
                machinery_type=req["machinery_type"],
                city=req["city"],
                province=req["province"],
                start_date=start,
                end_date=end,
                budget_per_day=req["budget_per_day"],
                status=req["status"],
                description=req["description"],
            )
            db.add(new_req)
            peticiones_creadas += 1
            if req["status"] == RequestStatus.OPEN:
                open_count += 1
            else:
                closed_count += 1
            print(
                f"  Creada: {req['machinery_type'].value:30s} en {req['city']:12s} "
                f"({req['status'].value.upper()}) — desde {(NOW + timedelta(days=req['start_date_offset'])).strftime('%d/%m/%Y')}"
            )

        db.commit()

        # ── Resumen ───────────────────────────────────────────────────────────
        print("\n" + "=" * 60)
        print(f"  Usuarios creados:           {usuarios_creados}")
        print(f"  Usuarios ya existentes:     {usuarios_existentes}")
        print(f"  Peticiones creadas:         {peticiones_creadas}")
        print(f"    - Estado OPEN:            {open_count}")
        print(f"    - Estado CLOSED:          {closed_count}")
        print(f"  Peticiones ya existentes:   {peticiones_existentes}")
        total_db = db.query(MachineryRequest).count()
        print(f"  Total peticiones en BD:     {total_db}")
        print("=" * 60)

    except Exception as e:
        db.rollback()
        print(f"\nERROR: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("Seed: demandas de maquinaria")
    run()
    print("\nListo.")
