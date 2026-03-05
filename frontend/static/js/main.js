/**
 * RentaMaq - JavaScript Principal
 * Gestiona la funcionalidad general de la aplicación
 */

// Configuración de la API
const API_BASE_URL = window.location.origin + '/api/v1';

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
    console.log('🚀 RentaMaq iniciado');
    
    // Verificar si hay sesión guardada
    checkAuthentication();
    
    // Cargar maquinaria inicial
    loadInitialMachinery();
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
            throw new Error(error.detail || 'Error en la petición');
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

/**
 * Carga la maquinaria inicial
 */
async function loadInitialMachinery() {
    const grid = document.getElementById('machineryGrid');
    const spinner = document.getElementById('loadingSpinner');
    
    try {
        spinner.style.display = 'block';
        grid.innerHTML = '';
        
        const data = await apiRequest('/machinery/search?limit=12');
        
        if (data.machinery && data.machinery.length > 0) {
            renderMachinery(data.machinery);
        } else {
            grid.innerHTML = '<p class="text-center">No hay maquinaria disponible en este momento.</p>';
        }
    } catch (error) {
        console.error('Error cargando maquinaria:', error);
        showAlert('Error al cargar la maquinaria', 'danger');
        grid.innerHTML = '<p class="text-center">Error al cargar la maquinaria. Por favor, intenta de nuevo.</p>';
    } finally {
        spinner.style.display = 'none';
    }
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