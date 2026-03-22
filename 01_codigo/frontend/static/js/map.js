/**
 * RentaMaq - Mapa de Maquinaria
 * Leaflet.js + OpenStreetMap (libre, sin API key)
 * Diseño tipo Booking.com: lista izquierda + mapa derecha
 */

let leafletMap = null;
let mapMarkers = {};      // machinery.id → marker L.marker
let activeMarkerId = null;
let isMapView = false;

// ── Coordenadas aproximadas de las principales ciudades españolas ──────────
const SPAIN_CITIES = {
    'madrid': [40.4168, -3.7038],
    'barcelona': [41.3851, 2.1734],
    'valencia': [39.4699, -0.3763],
    'sevilla': [37.3891, -5.9845],
    'seville': [37.3891, -5.9845],
    'zaragoza': [41.6488, -0.8891],
    'málaga': [36.7213, -4.4214],
    'malaga': [36.7213, -4.4214],
    'murcia': [37.9922, -1.1307],
    'palma': [39.5696, 2.6502],
    'las palmas': [28.1235, -15.4363],
    'bilbao': [43.2630, -2.9350],
    'alicante': [38.3453, -0.4831],
    'córdoba': [37.8882, -4.7794],
    'cordoba': [37.8882, -4.7794],
    'valladolid': [41.6528, -4.7245],
    'vigo': [42.2328, -8.7226],
    'gijón': [43.5453, -5.6615],
    'gijon': [43.5453, -5.6615],
    'granada': [37.1773, -3.5986],
    'vitoria': [42.8469, -2.6727],
    'gasteiz': [42.8469, -2.6727],
    'a coruña': [43.3623, -8.4115],
    'coruña': [43.3623, -8.4115],
    'elche': [38.2669, -0.6985],
    'oviedo': [43.3614, -5.8593],
    'badalona': [41.4500, 2.2472],
    'cartagena': [37.6257, -0.9966],
    'terrassa': [41.5641, 2.0082],
    'jerez': [36.6817, -6.1369],
    'sabadell': [41.5433, 2.1094],
    'getafe': [40.3057, -3.7329],
    'burgos': [42.3440, -3.6969],
    'almería': [36.8340, -2.4637],
    'almeria': [36.8340, -2.4637],
    'castellón': [39.9864, -0.0513],
    'castellon': [39.9864, -0.0513],
    'albacete': [38.9942, -1.8585],
    'salamanca': [40.9701, -5.6635],
    'logroño': [42.4627, -2.4449],
    'logro\u00f1o': [42.4627, -2.4449],
    'huelva': [37.2614, -6.9447],
    'badajoz': [38.8794, -6.9706],
    'tarragona': [41.1189, 1.2445],
    'león': [42.5987, -5.5671],
    'leon': [42.5987, -5.5671],
    'santander': [43.4623, -3.8099],
    'pamplona': [42.8169, -1.6432],
    'almendralejo': [38.6833, -6.4170],
    'mérida': [38.9162, -6.3437],
    'merida': [38.9162, -6.3437],
    'toledo': [39.8628, -4.0273],
    'guadalajara': [40.6326, -3.1659],
    'cuenca': [40.0704, -2.1374],
    'cáceres': [39.4753, -6.3724],
    'caceres': [39.4753, -6.3724],
    'soria': [41.7668, -2.4801],
    'teruel': [40.3456, -1.1065],
    'huesca': [42.1401, -0.4089],
    'lérida': [41.6175, 0.6200],
    'lleida': [41.6175, 0.6200],
    'gerona': [41.9794, 2.8214],
    'girona': [41.9794, 2.8214],
    'reus': [41.1547, 1.1070],
    'mataró': [41.5390, 2.4450],
    'mataro': [41.5390, 2.4450],
};

// ── Geocodificación: busca coordenadas por nombre de ciudad ──────────────────
async function getCoordinates(city, province) {
    const cityKey = city.toLowerCase().trim();
    // 1. Tabla de ciudades locales (instantáneo)
    if (SPAIN_CITIES[cityKey]) {
        return addJitter(SPAIN_CITIES[cityKey]);
    }
    // 2. Comprobar caché en localStorage
    const cacheKey = 'geo_' + cityKey.replace(/\s+/g, '_');
    const cached = localStorage.getItem(cacheKey);
    if (cached) {
        return addJitter(JSON.parse(cached));
    }
    // 3. Nominatim (OpenStreetMap, gratuito, sin clave)
    try {
        const query = `${city}, ${province}, España`;
        const url = `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(query)}&format=json&limit=1&countrycodes=es`;
        const res = await fetch(url, {
            headers: { 'Accept-Language': 'es', 'User-Agent': 'RentaMaq/1.0' }
        });
        const data = await res.json();
        if (data.length > 0) {
            const coords = [parseFloat(data[0].lat), parseFloat(data[0].lon)];
            localStorage.setItem(cacheKey, JSON.stringify(coords));
            return addJitter(coords);
        }
    } catch (e) {
        console.warn('Nominatim no disponible para:', city);
    }
    // 4. Fallback: centro de España con jitter
    return addJitter([40.4168, -3.7038]);
}

// Pequeño desplazamiento aleatorio para separar máquinas en la misma ciudad
function addJitter(coords) {
    const jitter = 0.008;
    return [
        coords[0] + (Math.random() - 0.5) * jitter,
        coords[1] + (Math.random() - 0.5) * jitter
    ];
}

// ── Icono de precio en el mapa (estilo Booking.com) ─────────────────────────
function createPriceIcon(price, isAvailable, isActive) {
    const bg = isActive ? '#004E89' : (isAvailable ? '#FF6B35' : '#adb5bd');
    const formatted = new Intl.NumberFormat('es-ES', {
        style: 'currency', currency: 'EUR', maximumFractionDigits: 0
    }).format(price);
    return L.divIcon({
        className: '',
        html: `<div class="map-price-marker" style="background:${bg}">${formatted}/día</div>`,
        iconAnchor: [40, 16],
        popupAnchor: [0, -20]
    });
}

// ── Construye el popup de una máquina ────────────────────────────────────────
function buildPopupContent(m) {
    const type = translateMachineryType(m.machinery_type);
    const price = formatPrice(m.daily_rate);
    const avail = m.is_available
        ? '<span style="color:#2ecc71;font-weight:700;">● Disponible</span>'
        : '<span style="color:#e74c3c;font-weight:700;">● No disponible</span>';
    return `
        <div class="map-popup">
            <strong>${m.title}</strong>
            <p style="margin:4px 0;color:#6c757d;font-size:0.85rem;">${type}${m.brand ? ' · ' + m.brand : ''}</p>
            <p style="margin:4px 0;font-size:0.85rem;">📍 ${m.location_city}, ${m.location_province}</p>
            <div style="display:flex;justify-content:space-between;align-items:center;margin-top:6px;">
                <strong style="color:#FF6B35;font-size:1rem;">${price}/día</strong>
                ${avail}
            </div>
            <button onclick="viewMachineryDetails(${m.id})"
                style="margin-top:8px;width:100%;padding:6px;background:#FF6B35;color:white;border:none;border-radius:6px;cursor:pointer;font-weight:600;">
                Ver Detalles
            </button>
        </div>`;
}

// ── Activar/desactivar marcador ──────────────────────────────────────────────
function setActiveMarker(id) {
    if (activeMarkerId && mapMarkers[activeMarkerId]) {
        const prev = mapMarkers[activeMarkerId];
        prev.setIcon(createPriceIcon(prev._machinery.daily_rate, prev._machinery.is_available, false));
        prev.setZIndexOffset(0);
    }
    if (id && mapMarkers[id]) {
        const m = mapMarkers[id];
        m.setIcon(createPriceIcon(m._machinery.daily_rate, m._machinery.is_available, true));
        m.setZIndexOffset(1000);
    }
    activeMarkerId = id;
}

// ── Inicializa el mapa Leaflet en el div permanente de la página ─────────────
function initMap() {
    if (leafletMap) return;
    if (!document.getElementById('leafletMap')) return;
    leafletMap = L.map('leafletMap', {
        center: [40.4168, -3.7038],
        zoom: 6,
        zoomControl: true
    });
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© <a href="https://openstreetmap.org/copyright">OpenStreetMap</a>',
        maxZoom: 18
    }).addTo(leafletMap);
}

// ── Puebla el mapa permanente con los marcadores de maquinaria ───────────────
async function populateMap(machineryList) {
    initMap();
    if (!leafletMap) return;

    // Limpiar marcadores previos
    Object.values(mapMarkers).forEach(m => m.remove());
    mapMarkers = {};

    const bounds = [];

    for (const m of machineryList) {
        let coords;
        if (m.latitude && m.longitude) {
            coords = [m.latitude, m.longitude];
        } else {
            coords = await getCoordinates(m.location_city, m.location_province);
        }

        const marker = L.marker(coords, {
            icon: createPriceIcon(m.daily_rate, m.is_available, false)
        }).addTo(leafletMap);
        marker._machinery = m;
        marker.bindPopup(buildPopupContent(m), { maxWidth: 260 });
        marker.on('click', () => setActiveMarker(m.id));
        mapMarkers[m.id] = marker;
        bounds.push(coords);
    }

    if (bounds.length > 0) {
        leafletMap.fitBounds(bounds, { padding: [50, 50], maxZoom: 10 });
    }

    leafletMap.invalidateSize();
}

// ── Muestra la vista de mapa tipo Booking.com (toggle desde lista) ───────────
async function showMapView(machineryList) {
    isMapView = true;

    const section = document.getElementById('machineryResults');
    section.innerHTML = `
        <div class="map-toggle-bar">
            <h2>Maquinaria Disponible <span class="map-count">${machineryList.length} resultados</span></h2>
            <div class="map-view-buttons">
                <button class="btn-view" onclick="switchToListView()" title="Vista lista">☰ Lista</button>
                <button class="btn-view active" title="Vista mapa">🗺️ Mapa</button>
            </div>
        </div>
        <div class="map-layout">
            <div class="map-sidebar" id="mapSidebar"></div>
            <div class="map-panel" id="mapPanel"></div>
        </div>`;

    // Mover el mapa permanente al panel del toggle (y restaurarlo al salir)
    const mapDiv = document.getElementById('leafletMap');
    document.getElementById('mapPanel').appendChild(mapDiv);

    if (!leafletMap) {
        initMap();
    }

    // Limpiar marcadores previos
    Object.values(mapMarkers).forEach(m => m.remove());
    mapMarkers = {};
    const sidebar = document.getElementById('mapSidebar');
    sidebar.innerHTML = '';

    const bounds = [];

    for (const m of machineryList) {
        let coords;
        if (m.latitude && m.longitude) {
            coords = [m.latitude, m.longitude];
        } else {
            coords = await getCoordinates(m.location_city, m.location_province);
        }

        const marker = L.marker(coords, {
            icon: createPriceIcon(m.daily_rate, m.is_available, false)
        }).addTo(leafletMap);
        marker._machinery = m;
        marker.bindPopup(buildPopupContent(m), { maxWidth: 260 });
        marker.on('click', () => {
            setActiveMarker(m.id);
            const card = document.getElementById('map-card-' + m.id);
            if (card) card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        });
        mapMarkers[m.id] = marker;
        bounds.push(coords);

        sidebar.appendChild(buildSidebarCard(m, marker, coords));
    }

    if (bounds.length > 0) {
        leafletMap.fitBounds(bounds, { padding: [40, 40], maxZoom: 10 });
    }

    setTimeout(() => leafletMap && leafletMap.invalidateSize(), 100);
}

// ── Tarjeta compacta para el sidebar del mapa ────────────────────────────────
function buildSidebarCard(m, marker, coords) {
    const div = document.createElement('div');
    div.id = 'map-card-' + m.id;
    div.className = 'map-sidebar-card';

    const imageUrl = m.images && m.images.length > 0
        ? m.images[0]
        : 'https://placehold.co/80x80/e9ecef/adb5bd?text=' + encodeURIComponent(m.machinery_type);

    div.innerHTML = `
        <img src="${imageUrl}" alt="${m.title}" class="map-card-img"
             onerror="this.src='https://placehold.co/80x80/e9ecef/adb5bd?text=Sin+foto'">
        <div class="map-card-info">
            <div class="map-card-title">${m.title}</div>
            <div class="map-card-meta">${translateMachineryType(m.machinery_type)}${m.brand ? ' · ' + m.brand : ''}</div>
            <div class="map-card-location">📍 ${m.location_city}, ${m.location_province}</div>
            <div class="map-card-footer">
                <span class="map-card-price">${formatPrice(m.daily_rate)}<small>/día</small></span>
                <span class="map-card-badge ${m.is_available ? 'avail' : 'unavail'}">
                    ${m.is_available ? 'Disponible' : 'No disponible'}
                </span>
            </div>
        </div>`;

    // Al pasar el ratón: resaltar marcador en el mapa
    div.addEventListener('mouseenter', () => {
        setActiveMarker(m.id);
        leafletMap.panTo(coords, { animate: true, duration: 0.5 });
    });
    div.addEventListener('mouseleave', () => setActiveMarker(null));

    // Al hacer clic: abrir popup y centrar mapa
    div.addEventListener('click', () => {
        leafletMap.setView(coords, 12, { animate: true });
        marker.openPopup();
        setActiveMarker(m.id);
    });

    return div;
}

// ── Vuelve a la vista de lista ───────────────────────────────────────────────
function switchToListView() {
    isMapView = false;
    if (leafletMap) {
        leafletMap.remove();
        leafletMap = null;
        mapMarkers = {};
    }
    loadInitialMachinery();
}
