/**
 * RentaMaq - JavaScript Principal
 * Gestiona la funcionalidad general de la aplicación
 */

// Configuración de la API
const API_BASE_URL = window.location.origin + '/api/v1';

// Avatar por defecto (SVG inline como data URI, sin dependencias externas)
const DEFAULT_AVATAR = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ccircle cx='50' cy='50' r='50' fill='%23e9ecef'/%3E%3Ccircle cx='50' cy='37' r='20' fill='%23adb5bd'/%3E%3Cellipse cx='50' cy='94' rx='34' ry='26' fill='%23adb5bd'/%3E%3C/svg%3E";

function getUserAvatar() {
    const userId = appState.currentUser && appState.currentUser.id;
    if (!userId) return DEFAULT_AVATAR;
    return localStorage.getItem('profile_photo_' + userId) || DEFAULT_AVATAR;
}

// Estado global de la aplicación
const appState = {
    currentUser: null,
    authToken: null,
    isAuthenticated: false
};

/**
 * Inicializa la aplicación
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('RentaMaq iniciado');

    // Capturar tokens de Google SSO si vienen en la URL
    const urlParams = new URLSearchParams(window.location.search);
    const accessToken = urlParams.get('access_token');
    const refreshToken = urlParams.get('refresh_token');
    const userId = urlParams.get('user_id');
    if (accessToken && refreshToken) {
        // Guardamos tokens en localStorage para persistencia entre recargas
        localStorage.setItem('access_token', accessToken);
        localStorage.setItem('refresh_token', refreshToken);

        // IMPORTANTE: asignar el token al estado ANTES de llamar a apiRequest,
        // porque apiRequest lee appState.authToken para construir la cabecera
        // Authorization. Si no se asigna aquí, la petición sale sin token → 401.
        appState.authToken = accessToken;

        // Limpiamos los tokens de la URL para no exponerlos en el historial
        // (buena práctica de seguridad OAuth2: RFC 6749 §10.6)
        window.history.replaceState({}, document.title, '/');

        // Obtenemos el perfil completo del usuario desde el backend
        apiRequest('/auth/me').then(user => {
            localStorage.setItem('current_user', JSON.stringify(user));
            appState.currentUser = user;
            appState.isAuthenticated = true;
            updateNavbarForAuthenticatedUser();
            showAlert('¡Bienvenido, ' + user.full_name + '!', 'success');
            showDashboard();
        }).catch(err => {
            // Si falla (token inválido, expirado, etc.) limpiamos el estado
            // y mostramos un error descriptivo en lugar del genérico de sesión
            console.error('Error cargando perfil tras Google SSO:', err);
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            appState.authToken = null;
            showAlert('No se pudo cargar tu perfil de Google. Inténtalo de nuevo.', 'danger');
        });
        return;
    }

    // Verificar si hay sesión guardada
    checkAuthentication();

    // Cargar maquinaria inicial
    loadInitialMachinery();

    // Inicializar el mapa permanente (sin necesidad de login)
    initMap();
});

/**
 * Verifica si el usuario está autenticado
 */
function checkAuthentication() {
    const token = localStorage.getItem('access_token');
    const user = localStorage.getItem('current_user');
    
    if (token && user) {
        appState.authToken = token;
        appState.currentUser = JSON.parse(user);
        appState.isAuthenticated = true;
        updateNavbarForAuthenticatedUser();
    }
}

/**
 * Actualiza la barra de navegación para usuario autenticado
 */
function updateNavbarForAuthenticatedUser() {
    const navbarMenu = document.getElementById('navbarMenu');
    const navbarMenuAuth = document.getElementById('navbarMenuAuth');
    
    if (appState.isAuthenticated) {
        navbarMenu.style.display = 'none';
        navbarMenuAuth.style.display = 'flex';
        // Actualizar avatar y nombre en navbar
        const navAvatar = document.getElementById('navAvatar');
        const navUserName = document.getElementById('navUserName');
        if (navAvatar) navAvatar.src = getUserAvatar();
        if (navUserName && appState.currentUser) {
            navUserName.textContent = appState.currentUser.full_name.split(' ')[0];
        }
        updateUnreadBadge();
        // Mostrar boton de publicar operario si esta en la seccion de operarios
        const btnPubOp = document.getElementById('btnPublishOperator');
        if (btnPubOp) btnPubOp.style.display = '';
    } else {
        navbarMenu.style.display = 'flex';
        navbarMenuAuth.style.display = 'none';
    }
}

/**
 * Realiza una petición a la API
 */
async function apiRequest(endpoint, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json'
        }
    };
    
    // Agregar token de autenticación si está disponible
    if (appState.authToken) {
        defaultOptions.headers['Authorization'] = `Bearer ${appState.authToken}`;
    }
    
    const finalOptions = {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...options.headers
        }
    };
    
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, finalOptions);
        
        // Si es 401, el token expiró
        if (response.status === 401) {
            handleUnauthorized();
            throw new Error('Sesión expirada');
        }
        
        if (!response.ok) {
            const error = await response.json();
            let errorMessage;
            if (Array.isArray(error.detail)) {
                errorMessage = error.detail.map(e => e.msg).join(', ');
            } else {
                errorMessage = error.detail || 'Error en la petición';
            }
            throw new Error(errorMessage);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error en API:', error);
        throw error;
    }
}

/**
 * Maneja sesiones no autorizadas
 */
function handleUnauthorized() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('current_user');
    appState.authToken = null;
    appState.currentUser = null;
    appState.isAuthenticated = false;
    updateNavbarForAuthenticatedUser();
    showAlert('Tu sesión ha expirado. Por favor, inicia sesión nuevamente.', 'danger');
}

/**
 * Muestra una alerta al usuario
 */
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    alertDiv.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 9999; max-width: 400px;';
    
    document.body.appendChild(alertDiv);
    
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

/**
 * Formatea un precio en euros
 */
function formatPrice(price) {
    return new Intl.NumberFormat('es-ES', {
        style: 'currency',
        currency: 'EUR'
    }).format(price);
}

/**
 * Formatea una fecha
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('es-ES', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    }).format(date);
}

/**
 * Traduce el tipo de maquinaria al español
 */
function translateMachineryType(type) {
    const translations = {
        'excavadora': 'Excavadora',
        'retroexcavadora': 'Retroexcavadora',
        'bulldozer': 'Bulldozer',
        'motoniveladora': 'Motoniveladora',
        'pala_cargadora': 'Pala Cargadora',
        'dumper': 'Dumper',
        'manipulador_telescopico': 'Manipulador Telescopico',
        'carretilla_elevadora': 'Carretilla Elevadora',
        'montacargas': 'Montacargas',
        'compactadora': 'Compactadora',
        'grua_torre': 'Grua Torre',
        'camion_grua': 'Camion Grua',
        'plataforma_elevadora': 'Plataforma Elevadora',
        'hormigonera': 'Hormigonera',
        'bomba_hormigon': 'Bomba de Hormigon',
        'martillo_hidraulico': 'Martillo Hidraulico',
        'cortadora_asfalto': 'Cortadora de Asfalto',
        'compresor': 'Compresor',
        'generador': 'Generador',
        'andamio': 'Andamio',
    };

    return translations[type] || type;
}

// Lista actual de maquinaria (compartida con map.js para el toggle de vista)
let currentMachineryList = [];
let activeTypeFilter = '';
let dateFilterActive = false;
let isLoadingMachinery = false;
let userCoordinates = null;   // {lat, lng} del usuario
let activeDistanceKm = null;  // null = sin filtro

/**
 * Carga la maquinaria inicial y activa los botones de vista lista/mapa
 */
async function loadInitialMachinery() {
    if (isLoadingMachinery) return;
    isLoadingMachinery = true;

    const grid = document.getElementById('machineryGrid');
    const spinner = document.getElementById('loadingSpinner');

    // Si estamos en vista mapa, destruirla y volver a lista
    if (typeof leafletMap !== 'undefined' && leafletMap) {
        leafletMap.remove();
        leafletMap = null;
        mapMarkers = {};
    }

    // Restaurar el contenedor de lista si fue reemplazado por el mapa
    const results = document.getElementById('machineryResults');
    if (!document.getElementById('machineryGrid')) {
        results.innerHTML = `
            <div class="results-header">
                <h2 class="mb-3">Maquinaria Disponible</h2>
                <div class="map-view-buttons" id="viewToggleButtons" style="display:none;">
                    <button class="btn-view active" id="btnListView" onclick="switchToListView()" title="Vista lista">☰ Lista</button>
                    <button class="btn-view" id="btnMapView" onclick="switchToMapViewFromList()" title="Vista mapa">🗺️ Mapa</button>
                </div>
            </div>
            <div class="card-grid" id="machineryGrid"></div>
            <div id="loadingSpinner" style="display:none;">
                <div class="spinner"></div>
                <p class="text-center">Cargando maquinaria...</p>
            </div>`;
    }

    const gridEl = document.getElementById('machineryGrid');
    const spinnerEl = document.getElementById('loadingSpinner');

    try {
        spinnerEl.style.display = 'block';
        gridEl.innerHTML = '';

        const data = await apiRequest('/machinery/search?limit=50');

        if (data.machinery && data.machinery.length > 0) {
            currentMachineryList = data.machinery;
            activeTypeFilter = '';
            dateFilterActive = false;
            renderMachinery(data.machinery);
            renderFilterBar();
            // Mostrar botones de vista lista/mapa
            const toggleBtns = document.getElementById('viewToggleButtons');
            if (toggleBtns) toggleBtns.style.display = 'flex';
            // Poblar el mapa permanente con los marcadores
            populateMap(data.machinery);
        } else {
            gridEl.innerHTML = '<p class="text-center">No hay maquinaria disponible en este momento.</p>';
        }
    } catch (error) {
        console.error('Error cargando maquinaria:', error);
        showAlert('Error al cargar la maquinaria', 'danger');
        gridEl.innerHTML = '<p class="text-center">Error al cargar la maquinaria. Por favor, intenta de nuevo.</p>';
    } finally {
        isLoadingMachinery = false;
        if (document.getElementById('loadingSpinner')) {
            document.getElementById('loadingSpinner').style.display = 'none';
        }
    }
}

/**
 * Cambia a vista mapa desde la vista lista (usando la lista cargada)
 */
function switchToMapViewFromList() {
    if (currentMachineryList.length === 0) {
        showAlert('No hay maquinaria para mostrar en el mapa', 'info');
        return;
    }
    showMapView(currentMachineryList);
}

/**
 * Renderiza las tarjetas de maquinaria
 */
function renderMachinery(machineryList) {
    const grid = document.getElementById('machineryGrid');
    grid.innerHTML = '';
    
    machineryList.forEach(machinery => {
        const card = createMachineryCard(machinery);
        grid.appendChild(card);
    });
}

/**
 * Crea una tarjeta de maquinaria
 */
function createMachineryCard(machinery) {
    const card = document.createElement('div');
    card.className = 'card';
    
    const imageUrl = machinery.images && machinery.images.length > 0 
        ? machinery.images[0] 
        : 'https://via.placeholder.com/300x200?text=' + encodeURIComponent(machinery.title);
    
    card.innerHTML = `
        <img src="${imageUrl}" alt="${machinery.title}" class="card-image" 
             onerror="this.src='https://via.placeholder.com/300x200?text=Sin+Imagen'">
        <div class="card-body">
            <h3 class="card-title">${machinery.title}</h3>
            <p class="card-text">
                <span class="badge badge-info">${translateMachineryType(machinery.machinery_type)}</span>
                ${machinery.brand ? `<span class="badge badge-secondary">${machinery.brand}</span>` : ''}
            </p>
            <p class="card-text">${machinery.description.substring(0, 100)}...</p>
            <p class="card-text">
                <strong>📍 ${machinery.location_city}, ${machinery.location_province}</strong>
            </p>
            <div class="card-footer">
                <div>
                    <strong>${formatPrice(machinery.daily_rate)}/día</strong>
                </div>
                <div>
                    ${machinery.is_available 
                        ? '<span class="badge badge-success">Disponible</span>' 
                        : '<span class="badge badge-warning">No disponible</span>'}
                </div>
            </div>
            <button class="btn btn-primary mt-2" style="width: 100%;" onclick="viewMachineryDetails(${machinery.id})">
                Ver Detalles
            </button>
        </div>
    `;
    
    return card;
}

/**
 * Ver detalles de una maquinaria
 */
async function viewMachineryDetails(machineryId) {
    try {
        const machinery = await apiRequest(`/machinery/${machineryId}`);
        showMachineryModal(machinery);
    } catch (error) {
        showAlert('Error al cargar los detalles', 'danger');
    }
}

/**
 * Muestra un modal con detalles de la maquinaria y verificación de disponibilidad
 */
function showMachineryModal(machinery) {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.id = 'machineryDetailModal';

    const images = machinery.images && machinery.images.length > 0 ? machinery.images : [];
    const imgUrl = images[0] || 'https://via.placeholder.com/600x300?text=' + encodeURIComponent(machinery.title);

    modal.innerHTML = `
        <div class="modal-dialog modal-lg">
            <div class="modal-header">
                <h3>${machinery.title}</h3>
                <button class="modal-close" onclick="document.getElementById('machineryDetailModal').remove()">✕</button>
            </div>
            <div class="modal-body">
                <img src="${imgUrl}" alt="${machinery.title}" style="width:100%;height:220px;object-fit:cover;border-radius:var(--border-radius);margin-bottom:1rem;"
                     onerror="this.src='https://via.placeholder.com/600x220?text=Sin+Imagen'">

                <div style="display:flex;gap:0.5rem;flex-wrap:wrap;margin-bottom:1rem;">
                    <span class="badge badge-info">${translateMachineryType(machinery.machinery_type)}</span>
                    ${machinery.brand ? `<span class="badge badge-secondary">${machinery.brand} ${machinery.model || ''}</span>` : ''}
                    ${machinery.year ? `<span class="badge badge-secondary">${machinery.year}</span>` : ''}
                    ${machinery.is_available
                        ? '<span class="badge badge-success">Disponible</span>'
                        : '<span class="badge badge-warning">No disponible</span>'}
                </div>

                <p style="color:var(--gray-700);margin-bottom:1rem;">${machinery.description}</p>

                <div class="detail-info-grid">
                    <div><span class="detail-label">Ubicación</span><span>📍 ${machinery.location_city}, ${machinery.location_province}</span></div>
                    <div><span class="detail-label">Precio diario</span><span><strong>${formatPrice(machinery.daily_rate)}</strong></span></div>
                    ${machinery.weekly_rate ? `<div><span class="detail-label">Precio semanal</span><span>${formatPrice(machinery.weekly_rate)}</span></div>` : ''}
                    ${machinery.monthly_rate ? `<div><span class="detail-label">Precio mensual</span><span>${formatPrice(machinery.monthly_rate)}</span></div>` : ''}
                    <div><span class="detail-label">Depósito</span><span>${formatPrice(machinery.deposit)}</span></div>
                    <div><span class="detail-label">Entrega</span><span>${machinery.delivery_available ? '✅ Disponible' : '❌ No disponible'}</span></div>
                </div>

                <!-- Verificar disponibilidad -->
                <div class="availability-section" id="availSection_${machinery.id}">
                    <h4 style="margin-bottom:0.75rem;">Verificar Disponibilidad</h4>
                    <div class="avail-date-row">
                        <div class="form-group" style="flex:1;margin:0;">
                            <label style="font-size:0.85rem;">Fecha inicio</label>
                            <input type="date" class="form-control" id="availStart_${machinery.id}">
                        </div>
                        <div class="form-group" style="flex:1;margin:0;">
                            <label style="font-size:0.85rem;">Fecha fin</label>
                            <input type="date" class="form-control" id="availEnd_${machinery.id}">
                        </div>
                        <button class="btn btn-secondary" style="align-self:flex-end;" onclick="checkAvailability(${machinery.id})">Consultar</button>
                    </div>
                    <div id="availResult_${machinery.id}" style="margin-top:0.75rem;"></div>
                </div>

                <!-- Chat con el propietario / Consultas recibidas -->
                ${!appState.isAuthenticated ? `
                <div class="alert alert-info" style="margin-top:1rem;margin-bottom:0;">
                    <a href="#" onclick="closeMachineryModal();showLogin()">Inicia sesion</a> para contactar al propietario
                </div>` : appState.currentUser.id === machinery.owner_id ? `
                <div class="chat-section" id="chatSection_${machinery.id}">
                    <div class="chat-header">
                        <span>Consultas recibidas sobre esta maquina</span>
                    </div>
                    <div id="ownerInquiries_${machinery.id}" style="padding:0.75rem;max-height:220px;overflow-y:auto;">
                        <div style="text-align:center;color:var(--gray-500);font-size:0.85rem;">Cargando...</div>
                    </div>
                </div>` : `
                <div class="chat-section" id="chatSection_${machinery.id}">
                    <div class="chat-header">
                        <span>Contactar al propietario</span>
                    </div>
                    <div class="chat-messages" id="chatMessages_${machinery.id}">
                        <div style="text-align:center;padding:1rem;color:var(--gray-500);font-size:0.85rem;">Cargando mensajes...</div>
                    </div>
                    <div class="chat-input-row">
                        <input type="text" class="form-control" id="chatInput_${machinery.id}"
                               placeholder="Escribe un mensaje..." maxlength="2000"
                               onkeydown="if(event.key==='Enter')sendChatMessage(${machinery.id},${machinery.owner_id})">
                        <button class="btn btn-primary btn-sm" onclick="sendChatMessage(${machinery.id},${machinery.owner_id})">Enviar</button>
                    </div>
                </div>`}

                <div style="display:flex;gap:0.5rem;margin-top:1.5rem;flex-wrap:wrap;">
                    ${appState.isAuthenticated
                        ? `<button class="btn btn-primary" onclick="initiateBooking(${machinery.id}); document.getElementById('machineryDetailModal').remove();">Reservar Ahora</button>`
                        : ''}
                    <button class="btn btn-secondary" onclick="closeMachineryModal()">Cerrar</button>
                </div>
            </div>
        </div>
    `;

    document.body.appendChild(modal);
    modal.addEventListener('click', e => { if (e.target === modal) closeMachineryModal(); });

    // Iniciar chat segun rol
    if (appState.isAuthenticated) {
        if (appState.currentUser.id === machinery.owner_id) {
            loadOwnerInquiries(machinery.id);
        } else {
            startChatPolling(machinery.id, machinery.owner_id);
        }
    }

    // Set min date to today
    const today = new Date().toISOString().split('T')[0];
    const startEl = document.getElementById(`availStart_${machinery.id}`);
    const endEl = document.getElementById(`availEnd_${machinery.id}`);
    if (startEl) { startEl.min = today; startEl.value = today; }
    if (endEl) {
        const next30 = new Date();
        next30.setDate(next30.getDate() + 30);
        endEl.min = today;
        endEl.value = next30.toISOString().split('T')[0];
    }

    // Cargar el calendario de disponibilidad automaticamente al abrir
    checkAvailability(machinery.id);
}

/**
 * Consulta la disponibilidad de una máquina en un rango y muestra un mini calendario
 */
async function checkAvailability(machineryId) {
    const startEl = document.getElementById(`availStart_${machineryId}`);
    const endEl = document.getElementById(`availEnd_${machineryId}`);
    const resultEl = document.getElementById(`availResult_${machineryId}`);

    if (!startEl || !endEl || !resultEl) return;
    const start = startEl.value;
    const end = endEl.value;

    if (!start || !end || end < start) {
        resultEl.innerHTML = '<p style="color:var(--danger-color);">Selecciona un rango de fechas válido.</p>';
        return;
    }

    resultEl.innerHTML = '<div class="spinner-sm"></div>';

    try {
        const data = await apiRequest(`/machinery/${machineryId}/availability?start_date=${start}&end_date=${end}`);
        resultEl.innerHTML = renderAvailabilityCalendar(data.availability, start, end);
    } catch (e) {
        resultEl.innerHTML = '<p style="color:var(--danger-color);">Error al consultar disponibilidad.</p>';
    }
}

/**
 * Renderiza un mini calendario de disponibilidad
 */
function renderAvailabilityCalendar(availability, start, end) {
    const dates = Object.keys(availability).sort();
    if (dates.length === 0) return '<p>Sin datos de disponibilidad.</p>';

    const counts = { available: 0, booked: 0, maintenance: 0 };
    dates.forEach(d => counts[availability[d]]++);

    const cells = dates.map(d => {
        const status = availability[d];
        const cls = status === 'available' ? 'avail-day-ok' : status === 'booked' ? 'avail-day-booked' : 'avail-day-maint';
        const label = d.split('-').slice(1).join('/'); // MM/DD
        return `<div class="avail-day ${cls}" title="${d}: ${status === 'available' ? 'Disponible' : status === 'booked' ? 'Reservado' : 'Mantenimiento'}">${parseInt(d.split('-')[2])}</div>`;
    }).join('');

    const allAvailable = counts.booked === 0 && counts.maintenance === 0;

    return `
        <div class="avail-calendar-wrap">
            <div class="avail-days-grid">${cells}</div>
            <div class="avail-legend">
                <span class="avail-dot avail-ok"></span> Disponible (${counts.available})
                <span class="avail-dot avail-booked" style="margin-left:0.75rem;"></span> Reservado (${counts.booked})
                <span class="avail-dot avail-maint" style="margin-left:0.75rem;"></span> Mantenimiento (${counts.maintenance})
            </div>
            ${allAvailable
                ? '<p style="color:var(--success-color);font-weight:600;margin-top:0.5rem;">✅ Todas las fechas seleccionadas están disponibles</p>'
                : '<p style="color:var(--warning-color);margin-top:0.5rem;">⚠️ Algunas fechas no están disponibles en el rango seleccionado</p>'}
        </div>
    `;
}

/**
 * Scroll suave al buscador
 */
function scrollToSearch() {
    document.getElementById('searchBox').scrollIntoView({ behavior: 'smooth' });
}

// ===== FILTER BAR (tipo + disponibilidad por fechas) =====

const MACHINERY_TYPES = [
    ['', 'Todas'],
    // Excavacion y movimiento de tierras
    ['excavadora', 'Excavadora'],
    ['retroexcavadora', 'Retroexcavadora'],
    ['bulldozer', 'Bulldozer'],
    ['motoniveladora', 'Motoniveladora'],
    // Carga y transporte
    ['pala_cargadora', 'Pala Cargadora'],
    ['dumper', 'Dumper'],
    ['manipulador_telescopico', 'Manipulador Telescopico'],
    ['carretilla_elevadora', 'Carretilla Elevadora'],
    ['montacargas', 'Montacargas'],
    // Compactacion
    ['compactadora', 'Compactadora'],
    // Elevacion
    ['grua_torre', 'Grua Torre'],
    ['camion_grua', 'Camion Grua'],
    ['plataforma_elevadora', 'Plataforma Elevadora'],
    // Hormigon
    ['hormigonera', 'Hormigonera'],
    ['bomba_hormigon', 'Bomba de Hormigon'],
    // Demolicion y corte
    ['martillo_hidraulico', 'Martillo Hidraulico'],
    ['cortadora_asfalto', 'Cortadora de Asfalto'],
    // Auxiliares
    ['compresor', 'Compresor'],
    ['generador', 'Generador'],
    ['andamio', 'Andamio'],
];

function renderFilterBar() {
    const existing = document.getElementById('publicFilterBar');
    if (existing) existing.remove();

    const machineryResults = document.getElementById('machineryResults');
    const grid = document.getElementById('machineryGrid');
    if (!machineryResults || !grid) return;

    const today = new Date().toISOString().split('T')[0];
    const next14 = new Date();
    next14.setDate(next14.getDate() + 14);
    const next14str = next14.toISOString().split('T')[0];

    const chipsHtml = MACHINERY_TYPES.map(([val, label]) =>
        `<button class="chip ${val === activeTypeFilter ? 'chip-active' : ''}"
                 data-type="${val}"
                 onclick="applyTypeFilter('${val}')">${label}</button>`
    ).join('');

    const bar = document.createElement('div');
    bar.id = 'publicFilterBar';
    bar.className = 'public-filter-bar';
    bar.innerHTML = `
        <div class="filter-section">
            <span class="filter-section-label">Filtrar por tipo de maquina</span>
            <div class="filter-chips" id="typeFilterChips">${chipsHtml}</div>
        </div>
        <div class="filter-section">
            <span class="filter-section-label">Consultar disponibilidad por fechas</span>
            <div class="filter-avail-row">
                <div class="form-group" style="margin:0;flex:1;min-width:130px;">
                    <label style="font-size:0.78rem;color:var(--gray-600);">Desde</label>
                    <input type="date" class="form-control" id="pubFilterStart" min="${today}" value="${today}">
                </div>
                <div class="form-group" style="margin:0;flex:1;min-width:130px;">
                    <label style="font-size:0.78rem;color:var(--gray-600);">Hasta</label>
                    <input type="date" class="form-control" id="pubFilterEnd" min="${today}" value="${next14str}">
                </div>
                <button class="btn btn-secondary" style="align-self:flex-end;white-space:nowrap;" onclick="applyDateFilter()">
                    Ver disponibilidad
                </button>
                <button class="btn btn-outline-sm" id="clearDateFilterBtn" style="align-self:flex-end;display:${dateFilterActive ? 'inline-block' : 'none'};" onclick="clearDateFilter()">
                    Limpiar fechas
                </button>
            </div>
            <div id="dateFilterStatus" style="margin-top:0.5rem;font-size:0.85rem;"></div>
        </div>
    `;

    // Seccion de distancia (siempre visible)
    const distSection = document.createElement('div');
    distSection.className = 'filter-section';
    distSection.innerHTML = `
        <span class="filter-section-label">Filtrar por distancia</span>
        <div class="filter-distance-top">
            <button class="btn btn-secondary btn-sm" id="locBtn" onclick="requestUserLocation()">
                Usar mi ubicacion
            </button>
            <span id="userLocStatus" style="font-size:0.82rem;color:var(--gray-600);"></span>
            ${activeDistanceKm ? `<button class="btn-outline-sm" onclick="clearDistanceFilter()">✕ Limpiar</button>` : ''}
        </div>
        <div id="distanceControls" style="display:${userCoordinates ? 'flex' : 'none'};align-items:center;gap:0.75rem;margin-top:0.6rem;flex-wrap:wrap;">
            <input type="range" class="distance-slider" id="distanceSlider"
                   min="10" max="500" step="10" value="${activeDistanceKm || 100}"
                   oninput="document.getElementById('distanceVal').textContent=this.value+' km';applyDistanceFilter(parseInt(this.value))">
            <span class="distance-value" id="distanceVal">${activeDistanceKm || 100} km</span>
        </div>
        ${userCoordinates && activeDistanceKm ? `<div id="distanceStatus" style="font-size:0.82rem;color:var(--success-color);margin-top:0.3rem;"></div>` : ''}
    `;
    bar.appendChild(distSection);

    // Insertar antes del grid (despues del results-header)
    machineryResults.insertBefore(bar, grid);
}

// ── Helpers de distancia ─────────────────────────────────────────────────────

function haversineKm(lat1, lng1, lat2, lng2) {
    const R = 6371;
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLng = (lng2 - lng1) * Math.PI / 180;
    const a = Math.sin(dLat / 2) ** 2
        + Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * Math.sin(dLng / 2) ** 2;
    return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

function getMachineryCoords(m) {
    if (m.latitude && m.longitude) return [m.latitude, m.longitude];
    if (typeof SPAIN_CITIES !== 'undefined') {
        const key = (m.location_city || '').toLowerCase().trim();
        if (SPAIN_CITIES[key]) return SPAIN_CITIES[key];
        const provKey = (m.location_province || '').toLowerCase().trim();
        if (SPAIN_CITIES[provKey]) return SPAIN_CITIES[provKey];
    }
    return null;
}

function getFilteredList() {
    let list = activeTypeFilter
        ? currentMachineryList.filter(m => m.machinery_type === activeTypeFilter)
        : [...currentMachineryList];

    if (userCoordinates && activeDistanceKm) {
        list = list.filter(m => {
            const coords = getMachineryCoords(m);
            if (!coords) return true; // incluir si no hay coords
            const km = haversineKm(userCoordinates.lat, userCoordinates.lng, coords[0], coords[1]);
            return km <= activeDistanceKm;
        });
    }
    return list;
}

function requestUserLocation() {
    const btn = document.getElementById('locBtn');
    const status = document.getElementById('userLocStatus');
    if (btn) btn.textContent = 'Detectando...';

    if (!navigator.geolocation) {
        showAlert('Tu navegador no soporta geolocalizacion', 'danger');
        return;
    }
    navigator.geolocation.getCurrentPosition(
        pos => {
            userCoordinates = { lat: pos.coords.latitude, lng: pos.coords.longitude };
            activeDistanceKm = 100;
            renderFilterBar();
            // Activar controles y mostrar ubicacion
            const controls = document.getElementById('distanceControls');
            const statusEl = document.getElementById('userLocStatus');
            if (controls) controls.style.display = 'flex';
            if (statusEl) statusEl.textContent = `Ubicacion detectada (${pos.coords.latitude.toFixed(2)}, ${pos.coords.longitude.toFixed(2)})`;
            applyDistanceFilter(100);
        },
        () => {
            showAlert('No se pudo obtener tu ubicacion. Activa el permiso en el navegador.', 'warning');
            if (btn) btn.textContent = 'Usar mi ubicacion';
        }
    );
}

function applyDistanceFilter(km) {
    activeDistanceKm = km;
    if (!userCoordinates) return;

    const filtered = getFilteredList();
    renderMachinery(filtered);

    const statusEl = document.getElementById('distanceStatus');
    if (statusEl) statusEl.textContent = `${filtered.length} maquina${filtered.length !== 1 ? 's' : ''} en ${km} km`;
}

function clearDistanceFilter() {
    activeDistanceKm = null;
    renderFilterBar();
    renderMachinery(getFilteredList());
}

// ── Filtros tipo y fecha (actualizados para respetar distancia) ───────────────

function applyTypeFilter(type) {
    activeTypeFilter = type;
    dateFilterActive = false;

    // Actualizar chips
    document.querySelectorAll('#typeFilterChips .chip').forEach(btn => {
        btn.classList.toggle('chip-active', btn.getAttribute('data-type') === type);
    });

    // Limpiar estado de fechas
    const statusEl = document.getElementById('dateFilterStatus');
    if (statusEl) statusEl.innerHTML = '';
    const clearBtn = document.getElementById('clearDateFilterBtn');
    if (clearBtn) clearBtn.style.display = 'none';

    renderMachinery(getFilteredList());
}

async function applyDateFilter() {
    const startEl = document.getElementById('pubFilterStart');
    const endEl = document.getElementById('pubFilterEnd');
    if (!startEl || !endEl) return;

    const start = startEl.value;
    const end = endEl.value;

    if (!start || !end || end < start) {
        showAlert('Selecciona un rango de fechas valido', 'danger');
        return;
    }

    const statusEl = document.getElementById('dateFilterStatus');
    if (statusEl) statusEl.innerHTML = '<span style="color:var(--gray-600);">Consultando disponibilidad...</span>';

    const filtered = activeTypeFilter
        ? currentMachineryList.filter(m => m.machinery_type === activeTypeFilter)
        : currentMachineryList;

    // Batch: consultar disponibilidad de todas las maquinas en paralelo
    const results = await Promise.allSettled(
        filtered.map(m =>
            apiRequest(`/machinery/${m.id}/availability?start_date=${start}&end_date=${end}`)
                .then(data => {
                    const vals = Object.values(data.availability);
                    const allFree = vals.length > 0 && vals.every(v => v === 'available');
                    return { id: m.id, status: allFree ? 'available' : 'partial' };
                })
        )
    );

    const availMap = {};
    results.forEach(r => {
        if (r.status === 'fulfilled') availMap[r.value.id] = r.value.status;
    });

    dateFilterActive = true;
    renderMachineryWithAvailability(filtered, availMap, start, end);

    const availCount = Object.values(availMap).filter(v => v === 'available').length;
    if (statusEl) {
        statusEl.innerHTML = `
            <span style="color:var(--success-color);font-weight:600;">
                ${availCount} maquina${availCount !== 1 ? 's' : ''} disponible${availCount !== 1 ? 's' : ''}
                para ${formatDateShort(start)} - ${formatDateShort(end)}
            </span>`;
    }
    const clearBtn = document.getElementById('clearDateFilterBtn');
    if (clearBtn) clearBtn.style.display = 'inline-block';
}

function clearDateFilter() {
    dateFilterActive = false;
    const statusEl = document.getElementById('dateFilterStatus');
    if (statusEl) statusEl.innerHTML = '';
    const clearBtn = document.getElementById('clearDateFilterBtn');
    if (clearBtn) clearBtn.style.display = 'none';

    const filtered = activeTypeFilter
        ? currentMachineryList.filter(m => m.machinery_type === activeTypeFilter)
        : currentMachineryList;
    renderMachinery(filtered);
}

function renderMachineryWithAvailability(machineryList, availMap, start, end) {
    const grid = document.getElementById('machineryGrid');
    grid.innerHTML = '';
    machineryList.forEach(machinery => {
        const card = createMachineryCard(machinery);
        const avail = availMap[machinery.id];
        if (avail !== undefined) {
            const badge = document.createElement('div');
            badge.style.cssText = 'padding:0 0.75rem 0.5rem;';
            badge.innerHTML = avail === 'available'
                ? `<span class="badge badge-success" style="font-size:0.8rem;">Libre ${formatDateShort(start)}-${formatDateShort(end)}</span>`
                : `<span class="badge badge-warning" style="font-size:0.8rem;">Ocupado parcialmente</span>`;
            const footer = card.querySelector('.card-footer');
            if (footer) footer.parentNode.insertBefore(badge, footer);
        }
        grid.appendChild(card);
    });
}

function formatDateShort(dateStr) {
    const [, m, d] = dateStr.split('-');
    return `${d}/${m}`;
}

// ===== CHAT / MENSAJERIA =====

let chatPollInterval = null;
let chatCurrentMachineryId = null;
let chatCurrentOtherId = null;

function closeMachineryModal() {
    stopChatPolling();
    const modal = document.getElementById('machineryDetailModal');
    if (modal) modal.remove();
}

async function loadChatMessages(machineryId, otherUserId) {
    const container = document.getElementById(`chatMessages_${machineryId}`);
    if (!container) return;
    try {
        const msgs = await apiRequest(`/messages/conversation/${machineryId}/${otherUserId}`);
        renderChatMessages(msgs, machineryId);
        updateUnreadBadge();
    } catch (e) {
        // silencioso si hay error de red en el poll
    }
}

function renderChatMessages(msgs, machineryId) {
    const container = document.getElementById(`chatMessages_${machineryId}`);
    if (!container) return;

    if (msgs.length === 0) {
        container.innerHTML = '<div style="text-align:center;padding:1.5rem;color:var(--gray-500);font-size:0.85rem;">Sin mensajes. Escribe el primero.</div>';
        return;
    }

    const myId = appState.currentUser.id;
    container.innerHTML = msgs.map(msg => {
        const isOwn = msg.sender_id === myId;
        const time = new Date(msg.created_at).toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' });
        const date = new Date(msg.created_at).toLocaleDateString('es-ES', { day: '2-digit', month: '2-digit' });
        return `
            <div class="chat-bubble ${isOwn ? 'chat-own' : 'chat-other'}">
                <div class="chat-bubble-text">${escHtml2(msg.content)}</div>
                <div class="chat-bubble-time">${date} ${time}</div>
            </div>`;
    }).join('');

    // Scroll al ultimo mensaje
    container.scrollTop = container.scrollHeight;
}

function escHtml2(str) {
    return String(str)
        .replace(/&/g, '&amp;').replace(/</g, '&lt;')
        .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

async function sendChatMessage(machineryId, ownerId) {
    const input = document.getElementById(`chatInput_${machineryId}`);
    if (!input) return;
    const content = input.value.trim();
    if (!content) return;

    input.disabled = true;
    try {
        await apiRequest('/messages', {
            method: 'POST',
            body: JSON.stringify({ receiver_id: ownerId, machinery_id: machineryId, content })
        });
        input.value = '';
        await loadChatMessages(machineryId, ownerId);
    } catch (e) {
        showAlert('Error al enviar el mensaje: ' + e.message, 'danger');
    } finally {
        input.disabled = false;
        input.focus();
    }
}

function startChatPolling(machineryId, otherUserId) {
    stopChatPolling();
    chatCurrentMachineryId = machineryId;
    chatCurrentOtherId = otherUserId;
    loadChatMessages(machineryId, otherUserId);
    chatPollInterval = setInterval(() => {
        loadChatMessages(chatCurrentMachineryId, chatCurrentOtherId);
    }, 5000);
}

function stopChatPolling() {
    if (chatPollInterval) {
        clearInterval(chatPollInterval);
        chatPollInterval = null;
    }
}

async function loadOwnerInquiries(machineryId) {
    const container = document.getElementById(`ownerInquiries_${machineryId}`);
    if (!container) return;
    try {
        const convs = await apiRequest(`/messages/machine/${machineryId}/conversations`);
        if (!convs || convs.length === 0) {
            container.innerHTML = '<p style="text-align:center;color:var(--gray-500);font-size:0.85rem;padding:0.5rem;">Nadie ha enviado consultas sobre esta maquina todavia.</p>';
            return;
        }
        container.innerHTML = convs.map(c => `
            <div class="inbox-row" style="margin-bottom:0.4rem;padding:0.6rem 0.8rem;"
                 onclick="closeMachineryModal();openConversationFromInbox(${c.machinery_id},${c.other_user_id},'${escHtml2(c.other_user_name)}','${escHtml2(c.machinery_title)}')">
                <div class="inbox-avatar" style="width:34px;height:34px;font-size:0.9rem;">${c.other_user_name.charAt(0).toUpperCase()}</div>
                <div class="inbox-info">
                    <div class="inbox-name" style="font-size:0.88rem;">${escHtml2(c.other_user_name)}
                        ${c.unread_count > 0 ? `<span class="inbox-unread-badge">${c.unread_count}</span>` : ''}
                    </div>
                    <div class="inbox-preview">${escHtml2(c.last_message)}</div>
                </div>
                <div class="inbox-time">${new Date(c.last_message_at).toLocaleDateString('es-ES')}</div>
            </div>`).join('');
    } catch (e) {
        container.innerHTML = '<p style="color:var(--danger-color);font-size:0.85rem;">Error al cargar consultas.</p>';
    }
}

async function updateUnreadBadge() {
    if (!appState.isAuthenticated) return;
    try {
        const data = await apiRequest('/messages/unread-count');
        const badge = document.getElementById('msgUnreadBadge');
        if (badge) {
            badge.textContent = data.unread > 0 ? data.unread : '';
            badge.style.display = data.unread > 0 ? 'inline-flex' : 'none';
        }
    } catch (e) { /* ignorar */ }
}

async function showInbox() {
    if (!appState.isAuthenticated) { showLogin(); return; }

    const mainContent = document.getElementById('mainContent');
    mainContent.innerHTML = `
        <div class="container mt-4">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:1rem;">
                <h2>Mis Mensajes</h2>
                <button class="btn btn-secondary" onclick="showDashboard()">Volver al Panel</button>
            </div>
            <div id="inboxList"><div class="spinner"></div></div>
        </div>`;

    try {
        const conversations = await apiRequest('/messages/inbox');
        const list = document.getElementById('inboxList');
        if (!conversations || conversations.length === 0) {
            list.innerHTML = '<p class="text-center" style="color:var(--gray-600);padding:2rem;">No tienes mensajes aun.</p>';
            return;
        }
        list.innerHTML = conversations.map(c => `
            <div class="inbox-row" onclick="openConversationFromInbox(${c.machinery_id}, ${c.other_user_id}, '${escHtml2(c.other_user_name)}', '${escHtml2(c.machinery_title)}')">
                <div class="inbox-avatar">${c.other_user_name.charAt(0).toUpperCase()}</div>
                <div class="inbox-info">
                    <div class="inbox-name">${escHtml2(c.other_user_name)}
                        ${c.unread_count > 0 ? `<span class="inbox-unread-badge">${c.unread_count}</span>` : ''}
                    </div>
                    <div class="inbox-machinery">${escHtml2(c.machinery_title)}</div>
                    <div class="inbox-preview">${escHtml2(c.last_message)}</div>
                </div>
                <div class="inbox-time">${new Date(c.last_message_at).toLocaleDateString('es-ES')}</div>
            </div>`).join('');
    } catch (e) {
        showAlert('Error al cargar mensajes', 'danger');
    }
}

function openConversationFromInbox(machineryId, otherUserId, otherName, machineryTitle) {
    const mainContent = document.getElementById('mainContent');
    mainContent.innerHTML = `
        <div class="container mt-4" style="max-width:680px;">
            <div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:1rem;">
                <button class="btn btn-secondary btn-sm" onclick="showInbox()">Volver</button>
                <div>
                    <h3 style="margin:0;">${escHtml2(otherName)}</h3>
                    <span style="font-size:0.85rem;color:var(--gray-600);">${escHtml2(machineryTitle)}</span>
                </div>
            </div>
            <div class="chat-section" style="height:420px;">
                <div class="chat-messages" id="chatMessages_inbox" style="height:320px;"></div>
                <div class="chat-input-row">
                    <input type="text" class="form-control" id="chatInput_inbox"
                           placeholder="Escribe un mensaje..." maxlength="2000"
                           onkeydown="if(event.key==='Enter')sendInboxMessage(${machineryId},${otherUserId})">
                    <button class="btn btn-primary btn-sm" onclick="sendInboxMessage(${machineryId},${otherUserId})">Enviar</button>
                </div>
            </div>
        </div>`;

    // Cargar mensajes
    (async () => {
        const msgs = await apiRequest(`/messages/conversation/${machineryId}/${otherUserId}`);
        const container = document.getElementById('chatMessages_inbox');
        if (!container) return;
        const myId = appState.currentUser.id;
        if (msgs.length === 0) {
            container.innerHTML = '<div style="text-align:center;padding:1.5rem;color:var(--gray-500);font-size:0.85rem;">Sin mensajes.</div>';
        } else {
            container.innerHTML = msgs.map(msg => {
                const isOwn = msg.sender_id === myId;
                const time = new Date(msg.created_at).toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' });
                const date = new Date(msg.created_at).toLocaleDateString('es-ES', { day: '2-digit', month: '2-digit' });
                return `<div class="chat-bubble ${isOwn ? 'chat-own' : 'chat-other'}">
                    <div class="chat-bubble-text">${escHtml2(msg.content)}</div>
                    <div class="chat-bubble-time">${date} ${time}</div>
                </div>`;
            }).join('');
            container.scrollTop = container.scrollHeight;
        }
    })();
}

async function sendInboxMessage(machineryId, receiverId) {
    const input = document.getElementById('chatInput_inbox');
    if (!input) return;
    const content = input.value.trim();
    if (!content) return;
    input.disabled = true;
    try {
        await apiRequest('/messages', {
            method: 'POST',
            body: JSON.stringify({ receiver_id: receiverId, machinery_id: machineryId, content })
        });
        input.value = '';
        const msgs = await apiRequest(`/messages/conversation/${machineryId}/${receiverId}`);
        const container = document.getElementById('chatMessages_inbox');
        if (container) {
            const myId = appState.currentUser.id;
            container.innerHTML = msgs.map(msg => {
                const isOwn = msg.sender_id === myId;
                const time = new Date(msg.created_at).toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' });
                const date = new Date(msg.created_at).toLocaleDateString('es-ES', { day: '2-digit', month: '2-digit' });
                return `<div class="chat-bubble ${isOwn ? 'chat-own' : 'chat-other'}">
                    <div class="chat-bubble-text">${escHtml2(msg.content)}</div>
                    <div class="chat-bubble-time">${date} ${time}</div>
                </div>`;
            }).join('');
            container.scrollTop = container.scrollHeight;
        }
    } catch (e) {
        showAlert('Error al enviar: ' + e.message, 'danger');
    } finally {
        input.disabled = false;
        input.focus();
    }
}

/**
 * Cierra sesión
 */
function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('current_user');
    appState.authToken = null;
    appState.currentUser = null;
    appState.isAuthenticated = false;
    updateNavbarForAuthenticatedUser();
    showAlert('Sesión cerrada correctamente', 'success');
    window.location.href = '/';
}