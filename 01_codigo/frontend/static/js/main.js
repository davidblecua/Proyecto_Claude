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
        'dumper': 'Dumper',
        'pala_cargadora': 'Pala Cargadora',
        'hormigonera': 'Hormigonera',
        'camion_grua': 'Camión Grúa',
        'grua_torre': 'Grúa Torre',
        'manipulador_telescopico': 'Manipulador Telescópico',
        'plataforma_elevadora': 'Plataforma Elevadora',
        'carretilla_elevadora': 'Carretilla Elevadora',
        'compactadora': 'Compactadora',
        'bulldozer': 'Bulldozer',
        'martillo_hidraulico': 'Martillo Hidráulico',
        'generador': 'Generador',
        'compresor': 'Compresor'
    };
    
    return translations[type] || type;
}

// Lista actual de maquinaria (compartida con map.js para el toggle de vista)
let currentMachineryList = [];

/**
 * Carga la maquinaria inicial y activa los botones de vista lista/mapa
 */
async function loadInitialMachinery() {
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
            renderMachinery(data.machinery);
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
 * Muestra un modal con detalles de la maquinaria
 */
function showMachineryModal(machinery) {
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed; top: 0; left: 0; right: 0; bottom: 0;
        background: rgba(0,0,0,0.7); z-index: 9999;
        display: flex; align-items: center; justify-content: center;
        padding: 20px;
    `;
    
    modal.innerHTML = `
        <div style="background: white; border-radius: 8px; max-width: 800px; max-height: 90vh; overflow-y: auto; padding: 2rem;">
            <h2>${machinery.title}</h2>
            <p><strong>Tipo:</strong> ${translateMachineryType(machinery.machinery_type)}</p>
            <p><strong>Marca:</strong> ${machinery.brand || 'No especificada'}</p>
            <p><strong>Modelo:</strong> ${machinery.model || 'No especificado'}</p>
            <p><strong>Año:</strong> ${machinery.year || 'No especificado'}</p>
            <p><strong>Descripción:</strong> ${machinery.description}</p>
            <p><strong>Ubicación:</strong> ${machinery.location_city}, ${machinery.location_province}</p>
            <p><strong>Precio diario:</strong> ${formatPrice(machinery.daily_rate)}</p>
            ${machinery.weekly_rate ? `<p><strong>Precio semanal:</strong> ${formatPrice(machinery.weekly_rate)}</p>` : ''}
            ${machinery.monthly_rate ? `<p><strong>Precio mensual:</strong> ${formatPrice(machinery.monthly_rate)}</p>` : ''}
            <p><strong>Depósito:</strong> ${formatPrice(machinery.deposit)}</p>
            <p><strong>Entrega disponible:</strong> ${machinery.delivery_available ? 'Sí' : 'No'}</p>
            ${machinery.delivery_cost ? `<p><strong>Coste de entrega:</strong> ${formatPrice(machinery.delivery_cost)}</p>` : ''}
            
            <div class="mt-3">
                ${appState.isAuthenticated 
                    ? `<button class="btn btn-primary" onclick="initiateBooking(${machinery.id})">Reservar Ahora</button>` 
                    : '<p class="alert alert-info">Debes iniciar sesión para reservar</p>'}
                <button class="btn btn-secondary" onclick="this.closest('div[style*=fixed]').remove()">Cerrar</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
}

/**
 * Scroll suave al buscador
 */
function scrollToSearch() {
    document.getElementById('searchBox').scrollIntoView({ behavior: 'smooth' });
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