/**
 * RentaMaq — Internacionalización (i18n)
 * Idiomas: es (español), ca (catalán), en (inglés)
 */

const TRANSLATIONS = {
    es: {
        // ── Navbar ───────────────────────────────────────────────────────────
        nav_home:           "Inicio",
        nav_machinery:      "Maquinaria",
        nav_profiles:       "Tipos de perfil",
        nav_search:         "Buscar maquinaria",
        nav_operators:      "Operarios",
        nav_requests:       "Busco maquinaria",
        nav_map:            "Mapa",
        nav_login:          "Iniciar sesión",
        nav_register:       "Registrarse",
        nav_logout:         "Cerrar sesión",
        nav_dashboard:      "Mi panel",
        nav_my_machinery:   "Mis máquinas",
        nav_my_bookings:    "Mis reservas",
        nav_my_operators:   "Mis operarios",
        nav_messages:       "Mensajes",
        nav_profile:        "Mi perfil",
        nav_info:           "Información",
        // ── Hero ─────────────────────────────────────────────────────────────
        hero_title:         "Alquila maquinaria con operario",
        hero_subtitle:      "La plataforma que conecta empresas constructoras con maquinaria pesada y sus operarios especializados",
        hero_cta_search:    "Buscar maquinaria",
        hero_cta_publish:   "Publicar maquinaria",
        // ── Buscador ─────────────────────────────────────────────────────────
        search_title:       "Busca la maquinaria que necesitas",
        search_type_label:  "Tipo de máquina",
        search_type_all:    "Todas",
        search_city_label:  "Ciudad",
        search_price_label: "Precio máximo/día (€)",
        search_btn:         "Buscar",
        search_placeholder: "Tipo de maquinaria...",
        search_city:        "Ciudad",
        search_price_max:   "Precio máximo",
        search_button:      "Buscar",
        search_no_results:  "No se encontró maquinaria con estos filtros",
        search_loading:     "Buscando...",
        // ── Tabs ─────────────────────────────────────────────────────────────
        tab_machinery:      "Maquinaria",
        tab_operators:      "Operarios",
        tab_requests:       "Busco maquinaria",
        // ── Secciones ────────────────────────────────────────────────────────
        machinery_available:    "Maquinaria disponible",
        machinery_unavailable:  "No disponible",
        machinery_day:          "día",
        machinery_per_day:      "por día",
        machinery_publish:      "Publicar maquinaria",
        machinery_my_listings:  "Mis anuncios",
        requests_title:         "Demandas de maquinaria",
        requests_desc:          "Empresas y profesionales que buscan maquinaria para alquilar. Si eres proveedor, ponte en contacto con ellos.",
        operators_title:        "Operarios disponibles",
        // ── Mapa ─────────────────────────────────────────────────────────────
        map_title:              "Mapa de maquinaria",
        map_subtitle:           "Haz clic en un marcador para ver los detalles de la máquina",
        map_search_placeholder: "Busca por dirección, código postal o ciudad...",
        map_search_btn:         "Buscar",
        map_search_error:       "Ubicación no encontrada, intenta con otra búsqueda.",
        // ── Features ─────────────────────────────────────────────────────────
        features_title:   "¿Por qué elegir RentaMaq?",
        feature1_title:   "Maquinaria verificada",
        feature1_desc:    "Todo el equipo publicado pasa un proceso de verificación antes de aparecer en el catálogo.",
        feature2_title:   "Reserva en minutos",
        feature2_desc:    "Encuentra la maquinaria que necesitas y confirma tu reserva en menos de 5 minutos.",
        feature3_title:   "Soporte durante la obra",
        feature3_desc:    "Nuestro equipo está disponible durante todo el período de alquiler para resolver cualquier incidencia.",
        // ── Tipos de perfil ──────────────────────────────────────────────────
        profile_types_title:    "Tipos de perfil en RentaMaq",
        profile_types_subtitle: "Elige el perfil que mejor se adapta a tu actividad. Puedes cambiar tu rol desde tu panel de cuenta.",
        profile_back:           "Volver al inicio",
        profile_edit:           "Editar perfil",
        profile_language:       "Idioma preferido",
        profile_save:           "Guardar cambios",
        // ── Reservas ─────────────────────────────────────────────────────────
        booking_start_date:         "Fecha de inicio",
        booking_end_date:           "Fecha de fin",
        booking_total:              "Total",
        booking_confirm:            "Confirmar reserva",
        booking_cancel:             "Cancelar reserva",
        booking_status_pending:     "Pendiente",
        booking_status_confirmed:   "Confirmada",
        booking_status_cancelled:   "Cancelada",
        booking_status_completed:   "Completada",
        // ── Autenticación ────────────────────────────────────────────────────
        auth_login:        "Iniciar sesión",
        auth_register:     "Crear cuenta",
        auth_email:        "Correo electrónico",
        auth_password:     "Contraseña",
        auth_forgot:       "¿Olvidaste tu contraseña?",
        auth_no_account:   "¿No tienes cuenta?",
        auth_have_account: "¿Ya tienes cuenta?",
        // ── Valoraciones ─────────────────────────────────────────────────────
        review_title:      "Valoraciones",
        review_add:        "Dejar valoración",
        review_average:    "Valoración media",
        review_no_reviews: "Aún no hay valoraciones",
        // ── Errores ──────────────────────────────────────────────────────────
        error_required:       "Este campo es obligatorio",
        error_email_invalid:  "El correo electrónico no es válido",
        error_password_weak:  "La contraseña debe tener mínimo 8 caracteres, una mayúscula y un número",
        error_generic:        "Ha ocurrido un error, inténtalo de nuevo",
        // ── General ──────────────────────────────────────────────────────────
        general_loading: "Cargando...",
        general_save:    "Guardar",
        general_cancel:  "Cancelar",
        general_confirm: "Confirmar",
        general_delete:  "Eliminar",
        general_edit:    "Editar",
        general_close:   "Cerrar",
        general_back:    "Volver",
        general_yes:     "Sí",
        general_no:      "No",
        // ── Fotos de maquinaria ──────────────────────────────────────────────
        photos_label:         "Fotos de la máquina",
        photos_add:           "Añadir fotos",
        photos_add_more:      "Añadir más fotos",
        photos_hint:          "JPG, PNG o WebP · máx. 5 MB por foto · hasta 10 fotos",
        photos_min_required:  "Añade al menos 1 foto antes de publicar",
        photos_max_reached:   "Límite de 10 fotos alcanzado",
        photos_cover:         "Portada",
        photos_drag_hint:     "Arrastra para reordenar",
        photos_gallery_prev:  "Anterior",
        photos_gallery_next:  "Siguiente",
        // ── Footer ───────────────────────────────────────────────────────────
        footer_copy:    "© 2024 RentaMaq - Plataforma de Alquiler de Maquinaria",
        footer_docs:    "Documentación API",
        footer_terms:   "Términos",
        footer_privacy: "Privacidad",
        footer_contact: "Contacto",
    },

    ca: {
        // ── Navbar ───────────────────────────────────────────────────────────
        nav_home:           "Inici",
        nav_machinery:      "Maquinària",
        nav_profiles:       "Tipus de perfil",
        nav_search:         "Cercar maquinària",
        nav_operators:      "Operaris",
        nav_requests:       "Busco maquinària",
        nav_map:            "Mapa",
        nav_login:          "Iniciar sessió",
        nav_register:       "Registrar-se",
        nav_logout:         "Tancar sessió",
        nav_dashboard:      "El meu tauler",
        nav_my_machinery:   "Les meves màquines",
        nav_my_bookings:    "Les meves reserves",
        nav_my_operators:   "Els meus operaris",
        nav_messages:       "Missatges",
        nav_profile:        "El meu perfil",
        nav_info:           "Informació",
        // ── Hero ─────────────────────────────────────────────────────────────
        hero_title:         "Lloga maquinària amb operari",
        hero_subtitle:      "La plataforma que connecta empreses constructores amb maquinària pesant i els seus operaris especialitzats",
        hero_cta_search:    "Cercar maquinària",
        hero_cta_publish:   "Publicar maquinària",
        // ── Buscador ─────────────────────────────────────────────────────────
        search_title:       "Cerca la maquinària que necessites",
        search_type_label:  "Tipus de màquina",
        search_type_all:    "Totes",
        search_city_label:  "Ciutat",
        search_price_label: "Preu màxim/dia (€)",
        search_btn:         "Cercar",
        search_placeholder: "Tipus de maquinària...",
        search_city:        "Ciutat",
        search_price_max:   "Preu màxim",
        search_button:      "Cercar",
        search_no_results:  "No s'ha trobat maquinària amb aquests filtres",
        search_loading:     "Cercant...",
        // ── Tabs ─────────────────────────────────────────────────────────────
        tab_machinery:      "Maquinària",
        tab_operators:      "Operaris",
        tab_requests:       "Busco maquinària",
        // ── Secciones ────────────────────────────────────────────────────────
        machinery_available:    "Maquinària disponible",
        machinery_unavailable:  "No disponible",
        machinery_day:          "dia",
        machinery_per_day:      "per dia",
        machinery_publish:      "Publicar maquinària",
        machinery_my_listings:  "Els meus anuncis",
        requests_title:         "Demandes de maquinària",
        requests_desc:          "Empreses i professionals que busquen maquinària per llogar. Si ets proveïdor, posa't en contacte amb ells.",
        operators_title:        "Operaris disponibles",
        // ── Mapa ─────────────────────────────────────────────────────────────
        map_title:              "Mapa de maquinària",
        map_subtitle:           "Fes clic en un marcador per veure els detalls de la màquina",
        map_search_placeholder: "Cerca per adreça, codi postal o ciutat...",
        map_search_btn:         "Cercar",
        map_search_error:       "Ubicació no trobada, prova amb una altra cerca.",
        // ── Features ─────────────────────────────────────────────────────────
        features_title:   "Per què triar RentaMaq?",
        feature1_title:   "Maquinària verificada",
        feature1_desc:    "Tot l'equip publicat passa un procés de verificació abans d'aparèixer al catàleg.",
        feature2_title:   "Reserva en minuts",
        feature2_desc:    "Troba la maquinària que necessites i confirma la teva reserva en menys de 5 minuts.",
        feature3_title:   "Suport durant l'obra",
        feature3_desc:    "El nostre equip està disponible durant tot el període de lloguer per resoldre qualsevol incidència.",
        // ── Tipos de perfil ──────────────────────────────────────────────────
        profile_types_title:    "Tipus de perfil a RentaMaq",
        profile_types_subtitle: "Tria el perfil que millor s'adapta a la teva activitat. Pots canviar el teu rol des del teu tauler de compte.",
        profile_back:           "Tornar a l'inici",
        profile_edit:           "Editar perfil",
        profile_language:       "Idioma preferit",
        profile_save:           "Desar canvis",
        // ── Reservas ─────────────────────────────────────────────────────────
        booking_start_date:         "Data d'inici",
        booking_end_date:           "Data de fi",
        booking_total:              "Total",
        booking_confirm:            "Confirmar reserva",
        booking_cancel:             "Cancel·lar reserva",
        booking_status_pending:     "Pendent",
        booking_status_confirmed:   "Confirmada",
        booking_status_cancelled:   "Cancel·lada",
        booking_status_completed:   "Completada",
        // ── Autenticación ────────────────────────────────────────────────────
        auth_login:        "Iniciar sessió",
        auth_register:     "Crear compte",
        auth_email:        "Correu electrònic",
        auth_password:     "Contrasenya",
        auth_forgot:       "Has oblidat la contrasenya?",
        auth_no_account:   "No tens compte?",
        auth_have_account: "Ja tens compte?",
        // ── Valoraciones ─────────────────────────────────────────────────────
        review_title:      "Valoracions",
        review_add:        "Deixar valoració",
        review_average:    "Valoració mitjana",
        review_no_reviews: "Encara no hi ha valoracions",
        // ── Errores ──────────────────────────────────────────────────────────
        error_required:       "Aquest camp és obligatori",
        error_email_invalid:  "El correu electrònic no és vàlid",
        error_password_weak:  "La contrasenya ha de tenir mínim 8 caràcters, una majúscula i un número",
        error_generic:        "S'ha produït un error, torna-ho a intentar",
        // ── General ──────────────────────────────────────────────────────────
        general_loading: "Carregant...",
        general_save:    "Desar",
        general_cancel:  "Cancel·lar",
        general_confirm: "Confirmar",
        general_delete:  "Eliminar",
        general_edit:    "Editar",
        general_close:   "Tancar",
        general_back:    "Tornar",
        general_yes:     "Sí",
        general_no:      "No",
        // ── Fotos de maquinaria ──────────────────────────────────────────────
        photos_label:         "Fotos de la màquina",
        photos_add:           "Afegir fotos",
        photos_add_more:      "Afegir més fotos",
        photos_hint:          "JPG, PNG o WebP · màx. 5 MB per foto · fins a 10 fotos",
        photos_min_required:  "Afegeix almenys 1 foto abans de publicar",
        photos_max_reached:   "Límit de 10 fotos assolit",
        photos_cover:         "Portada",
        photos_drag_hint:     "Arrossega per reordenar",
        photos_gallery_prev:  "Anterior",
        photos_gallery_next:  "Següent",
        // ── Footer ───────────────────────────────────────────────────────────
        footer_copy:    "© 2024 RentaMaq - Plataforma de Lloguer de Maquinària",
        footer_docs:    "Documentació API",
        footer_terms:   "Termes",
        footer_privacy: "Privacitat",
        footer_contact: "Contacte",
    },

    en: {
        // ── Navbar ───────────────────────────────────────────────────────────
        nav_home:           "Home",
        nav_machinery:      "Machinery",
        nav_profiles:       "Profile types",
        nav_search:         "Search machinery",
        nav_operators:      "Operators",
        nav_requests:       "I need machinery",
        nav_map:            "Map",
        nav_login:          "Log in",
        nav_register:       "Sign up",
        nav_logout:         "Log out",
        nav_dashboard:      "My dashboard",
        nav_my_machinery:   "My machines",
        nav_my_bookings:    "My bookings",
        nav_my_operators:   "My operators",
        nav_messages:       "Messages",
        nav_profile:        "My profile",
        nav_info:           "Information",
        // ── Hero ─────────────────────────────────────────────────────────────
        hero_title:         "Rent machinery with operator",
        hero_subtitle:      "The platform connecting construction companies with heavy machinery and their specialized operators",
        hero_cta_search:    "Search machinery",
        hero_cta_publish:   "List machinery",
        // ── Buscador ─────────────────────────────────────────────────────────
        search_title:       "Find the machinery you need",
        search_type_label:  "Machine type",
        search_type_all:    "All",
        search_city_label:  "City",
        search_price_label: "Max price/day (€)",
        search_btn:         "Search",
        search_placeholder: "Machinery type...",
        search_city:        "City",
        search_price_max:   "Max price",
        search_button:      "Search",
        search_no_results:  "No machinery found with these filters",
        search_loading:     "Searching...",
        // ── Tabs ─────────────────────────────────────────────────────────────
        tab_machinery:      "Machinery",
        tab_operators:      "Operators",
        tab_requests:       "Looking for machinery",
        // ── Secciones ────────────────────────────────────────────────────────
        machinery_available:    "Available machinery",
        machinery_unavailable:  "Not available",
        machinery_day:          "day",
        machinery_per_day:      "per day",
        machinery_publish:      "List machinery",
        machinery_my_listings:  "My listings",
        requests_title:         "Machinery requests",
        requests_desc:          "Companies and professionals looking for machinery to rent. If you are a supplier, get in touch with them.",
        operators_title:        "Available operators",
        // ── Mapa ─────────────────────────────────────────────────────────────
        map_title:              "Machinery map",
        map_subtitle:           "Click on a marker to view machine details",
        map_search_placeholder: "Search by address, postcode or city...",
        map_search_btn:         "Search",
        map_search_error:       "Location not found, please try another search.",
        // ── Features ─────────────────────────────────────────────────────────
        features_title:   "Why choose RentaMaq?",
        feature1_title:   "Verified machinery",
        feature1_desc:    "All listed equipment goes through a verification process before appearing in the catalogue.",
        feature2_title:   "Book in minutes",
        feature2_desc:    "Find the machinery you need and confirm your booking in under 5 minutes.",
        feature3_title:   "On-site support",
        feature3_desc:    "Our team is available throughout the entire rental period to resolve any incident.",
        // ── Tipos de perfil ──────────────────────────────────────────────────
        profile_types_title:    "Profile types in RentaMaq",
        profile_types_subtitle: "Choose the profile that best fits your activity. You can change your role from your account panel.",
        profile_back:           "Back to home",
        profile_edit:           "Edit profile",
        profile_language:       "Preferred language",
        profile_save:           "Save changes",
        // ── Reservas ─────────────────────────────────────────────────────────
        booking_start_date:         "Start date",
        booking_end_date:           "End date",
        booking_total:              "Total",
        booking_confirm:            "Confirm booking",
        booking_cancel:             "Cancel booking",
        booking_status_pending:     "Pending",
        booking_status_confirmed:   "Confirmed",
        booking_status_cancelled:   "Cancelled",
        booking_status_completed:   "Completed",
        // ── Autenticación ────────────────────────────────────────────────────
        auth_login:        "Log in",
        auth_register:     "Create account",
        auth_email:        "Email address",
        auth_password:     "Password",
        auth_forgot:       "Forgot your password?",
        auth_no_account:   "Don't have an account?",
        auth_have_account: "Already have an account?",
        // ── Valoraciones ─────────────────────────────────────────────────────
        review_title:      "Reviews",
        review_add:        "Leave a review",
        review_average:    "Average rating",
        review_no_reviews: "No reviews yet",
        // ── Errores ──────────────────────────────────────────────────────────
        error_required:       "This field is required",
        error_email_invalid:  "The email address is not valid",
        error_password_weak:  "Password must be at least 8 characters, include one uppercase letter and one number",
        error_generic:        "An error occurred, please try again",
        // ── General ──────────────────────────────────────────────────────────
        general_loading: "Loading...",
        general_save:    "Save",
        general_cancel:  "Cancel",
        general_confirm: "Confirm",
        general_delete:  "Delete",
        general_edit:    "Edit",
        general_close:   "Close",
        general_back:    "Back",
        general_yes:     "Yes",
        general_no:      "No",
        // ── Fotos de maquinaria ──────────────────────────────────────────────
        photos_label:         "Machine photos",
        photos_add:           "Add photos",
        photos_add_more:      "Add more photos",
        photos_hint:          "JPG, PNG or WebP · max. 5 MB per photo · up to 10 photos",
        photos_min_required:  "Add at least 1 photo before publishing",
        photos_max_reached:   "10-photo limit reached",
        photos_cover:         "Cover",
        photos_drag_hint:     "Drag to reorder",
        photos_gallery_prev:  "Previous",
        photos_gallery_next:  "Next",
        // ── Footer ───────────────────────────────────────────────────────────
        footer_copy:    "© 2024 RentaMaq - Machinery Rental Platform",
        footer_docs:    "API Documentation",
        footer_terms:   "Terms",
        footer_privacy: "Privacy",
        footer_contact: "Contact",
    },
};

// ── Funciones i18n ────────────────────────────────────────────────────────────

function getLang() {
    return localStorage.getItem("rentamaq_lang") || "es";
}

function setLang(lang) {
    if (!["es", "ca", "en"].includes(lang)) return;
    localStorage.setItem("rentamaq_lang", lang);
    applyTranslations();
    updateLangSelector();
    const token = localStorage.getItem("access_token");
    if (token) {
        fetch("/api/v1/users/me/language", {
            method: "PATCH",
            headers: {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + token,
            },
            body: JSON.stringify({ language: lang }),
        }).catch(() => {});
    }
}

function applyTranslations() {
    const lang = getLang();
    const tr   = TRANSLATIONS[lang] || TRANSLATIONS["es"];
    document.querySelectorAll("[data-i18n]").forEach(el => {
        const key = el.getAttribute("data-i18n");
        const val = tr[key] || TRANSLATIONS["es"][key];
        if (!val) return;
        if (el.tagName === "INPUT" || el.tagName === "TEXTAREA") {
            el.placeholder = val;
        } else {
            el.textContent = val;
        }
    });
    document.querySelectorAll("[data-i18n-placeholder]").forEach(el => {
        const key = el.getAttribute("data-i18n-placeholder");
        const val = tr[key] || TRANSLATIONS["es"][key];
        if (val) el.placeholder = val;
    });
}

function t(key) {
    const lang = getLang();
    return (TRANSLATIONS[lang] && TRANSLATIONS[lang][key])
        || TRANSLATIONS["es"][key]
        || key;
}

function updateLangSelector() {
    const current = getLang();
    document.querySelectorAll(".lang-btn").forEach(btn => {
        const isActive = btn.getAttribute("data-lang") === current;
        btn.style.fontWeight     = isActive ? "700" : "400";
        btn.style.textDecoration = isActive ? "underline" : "none";
        btn.setAttribute("aria-pressed", isActive ? "true" : "false");
    });
}

document.addEventListener("DOMContentLoaded", () => {
    applyTranslations();
    updateLangSelector();
});
