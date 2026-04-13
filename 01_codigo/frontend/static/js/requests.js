/**
 * RentaMaq - Sistema de Demandas de Maquinaria
 * Permite a consumidores publicar necesidades de alquiler y a todos ver el listado.
 */

// ── Traducción de tipos de maquinaria (reutiliza la de search.js si existe) ──
function translateMachineryTypeReq(type) {
    const map = {
        excavadora: 'Excavadora', retroexcavadora: 'Retroexcavadora',
        bulldozer: 'Bulldozer', motoniveladora: 'Motoniveladora',
        pala_cargadora: 'Pala Cargadora', dumper: 'Dumper',
        manipulador_telescopico: 'Manipulador Telescópico',
        carretilla_elevadora: 'Carretilla Elevadora', montacargas: 'Montacargas',
        compactadora: 'Compactadora', grua_torre: 'Grúa Torre',
        camion_grua: 'Camión Grúa', plataforma_elevadora: 'Plataforma Elevadora',
        hormigonera: 'Hormigonera', bomba_hormigon: 'Bomba de Hormigón',
        martillo_hidraulico: 'Martillo Hidráulico', cortadora_asfalto: 'Cortadora de Asfalto',
        compresor: 'Compresor', generador: 'Generador', andamio: 'Andamio',
    };
    return map[type] || type;
}

// ── Cambiar a la pestaña de demandas ─────────────────────────────────────────
function showRequestsTab() {
    document.getElementById('machinerySection').style.display = 'none';
    document.getElementById('operatorsSection').style.display = 'none';
    document.getElementById('requestsSection').style.display = 'block';

    // Actualizar tabs activos
    ['tabMachinery', 'tabOperators', 'tabRequests'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.classList.remove('tab-active');
    });
    const tab = document.getElementById('tabRequests');
    if (tab) tab.classList.add('tab-active');

    // Mostrar botón de publicar si es consumer
    const btnPublish = document.getElementById('btnPublishRequest');
    if (btnPublish) {
        const isConsumer = appState.isAuthenticated &&
            appState.currentUser &&
            appState.currentUser.role === 'consumer';
        btnPublish.style.display = isConsumer ? 'inline-block' : 'none';
    }

    loadRequests();
}

// ── Cargar y renderizar listado de demandas ───────────────────────────────────
async function loadRequests() {
    const grid = document.getElementById('requestsGrid');
    if (!grid) return;
    grid.innerHTML = '<p style="color:var(--gray-500);">Cargando demandas...</p>';

    try {
        const data = await apiRequest('/requests?limit=50');
        renderRequestsList(data.requests || []);
    } catch (e) {
        grid.innerHTML = '<p style="color:var(--danger-color);">Error al cargar las demandas.</p>';
    }
}

function renderRequestsList(requests) {
    const grid = document.getElementById('requestsGrid');
    if (!grid) return;

    if (!requests.length) {
        grid.innerHTML = `
            <div style="text-align:center;padding:3rem;color:var(--gray-500);">
                <p style="font-size:1.1rem;margin-bottom:0.5rem;">No hay demandas abiertas en este momento.</p>
                <p>Si buscas maquinaria, publica tu demanda y los proveedores se pondrán en contacto contigo.</p>
            </div>`;
        return;
    }

    grid.innerHTML = requests.map(req => buildRequestCard(req)).join('');
}

function buildRequestCard(req) {
    const start = new Date(req.start_date).toLocaleDateString('es-ES');
    const end = new Date(req.end_date).toLocaleDateString('es-ES');
    const budget = req.budget_per_day
        ? `Presupuesto: <strong>${req.budget_per_day.toFixed(0)} €/día</strong>`
        : 'Sin presupuesto indicado';
    const author = req.user ? escHtml(req.user.full_name || req.user.username || '') : '';
    const created = new Date(req.created_at).toLocaleDateString('es-ES');

    const isAuthor = appState.isAuthenticated &&
        appState.currentUser &&
        appState.currentUser.id === req.user_id;

    return `
        <div class="request-card">
            <div class="request-card-header">
                <span class="badge badge-info">${escHtml(translateMachineryTypeReq(req.machinery_type))}</span>
                <span class="request-location">
                    ${escHtml(req.city)}, ${escHtml(req.province)}
                </span>
            </div>
            ${req.description
                ? `<p class="request-description">${escHtml(req.description)}</p>`
                : ''}
            <div class="request-meta">
                <span>Fechas: <strong>${start}</strong> al <strong>${end}</strong></span>
                <span>${budget}</span>
            </div>
            <div class="request-footer">
                <span class="request-author">Publicado por ${author} el ${created}</span>
                ${isAuthor
                    ? `<button class="btn btn-danger btn-sm" onclick="closeRequest(${req.id})">Cerrar demanda</button>`
                    : ''}
            </div>
        </div>`;
}

// ── Cerrar demanda ────────────────────────────────────────────────────────────
async function closeRequest(requestId) {
    if (!confirm('¿Cerrar esta demanda?')) return;
    try {
        await apiRequest(`/requests/${requestId}/close`, { method: 'PATCH' });
        showAlert('Demanda cerrada correctamente', 'success');
        loadRequests();
    } catch (e) {
        showAlert('Error al cerrar la demanda: ' + e.message, 'danger');
    }
}

// ── Formulario para publicar demanda ─────────────────────────────────────────
function showPublishRequest() {
    if (!appState.isAuthenticated) { showLogin(); return; }
    if (appState.currentUser.role !== 'consumer') {
        showAlert('Solo los consumidores pueden publicar demandas', 'warning');
        return;
    }

    const today = new Date().toISOString().split('T')[0];

    showModal(`
        <h3 style="margin-bottom:1.5rem;">Publicar demanda de maquinaria</h3>
        <form onsubmit="submitRequest(event)">
            <div class="form-group mb-2">
                <label>Tipo de maquinaria <span class="req">*</span></label>
                <select class="form-control" id="reqType" required>
                    <option value="">Selecciona un tipo...</option>
                    <optgroup label="Excavación">
                        <option value="excavadora">Excavadora</option>
                        <option value="retroexcavadora">Retroexcavadora</option>
                        <option value="bulldozer">Bulldozer</option>
                        <option value="motoniveladora">Motoniveladora</option>
                    </optgroup>
                    <optgroup label="Carga y transporte">
                        <option value="pala_cargadora">Pala Cargadora</option>
                        <option value="dumper">Dumper</option>
                        <option value="manipulador_telescopico">Manipulador Telescópico</option>
                        <option value="carretilla_elevadora">Carretilla Elevadora</option>
                        <option value="montacargas">Montacargas</option>
                    </optgroup>
                    <optgroup label="Compactación y nivelación">
                        <option value="compactadora">Compactadora</option>
                    </optgroup>
                    <optgroup label="Elevación">
                        <option value="grua_torre">Grúa Torre</option>
                        <option value="camion_grua">Camión Grúa</option>
                        <option value="plataforma_elevadora">Plataforma Elevadora</option>
                    </optgroup>
                    <optgroup label="Hormigón">
                        <option value="hormigonera">Hormigonera</option>
                        <option value="bomba_hormigon">Bomba de Hormigón</option>
                    </optgroup>
                    <optgroup label="Demolición">
                        <option value="martillo_hidraulico">Martillo Hidráulico</option>
                        <option value="cortadora_asfalto">Cortadora de Asfalto</option>
                    </optgroup>
                    <optgroup label="Auxiliares">
                        <option value="compresor">Compresor</option>
                        <option value="generador">Generador</option>
                        <option value="andamio">Andamio</option>
                    </optgroup>
                </select>
            </div>
            <div class="form-group mb-2">
                <label>Descripción de la necesidad</label>
                <textarea class="form-control" id="reqDesc" rows="3" maxlength="1000"
                    placeholder="Describe brevemente para qué la necesitas, condiciones especiales..."></textarea>
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.75rem;">
                <div class="form-group mb-2">
                    <label>Ciudad <span class="req">*</span></label>
                    <input type="text" class="form-control" id="reqCity" required placeholder="Barcelona">
                </div>
                <div class="form-group mb-2">
                    <label>Provincia <span class="req">*</span></label>
                    <input type="text" class="form-control" id="reqProvince" required placeholder="Barcelona">
                </div>
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.75rem;">
                <div class="form-group mb-2">
                    <label>Fecha inicio <span class="req">*</span></label>
                    <input type="date" class="form-control" id="reqStart" required min="${today}">
                </div>
                <div class="form-group mb-2">
                    <label>Fecha fin <span class="req">*</span></label>
                    <input type="date" class="form-control" id="reqEnd" required min="${today}">
                </div>
            </div>
            <div class="form-group mb-3">
                <label>Presupuesto por día (€) — opcional</label>
                <input type="number" class="form-control" id="reqBudget" min="0" placeholder="200">
            </div>
            <button type="submit" class="btn btn-primary" style="width:100%;">Publicar demanda</button>
        </form>`);
}

async function submitRequest(event) {
    event.preventDefault();
    const startVal = document.getElementById('reqStart').value;
    const endVal = document.getElementById('reqEnd').value;
    const budget = document.getElementById('reqBudget').value;

    const payload = {
        machinery_type: document.getElementById('reqType').value,
        description: document.getElementById('reqDesc').value.trim() || null,
        city: document.getElementById('reqCity').value.trim(),
        province: document.getElementById('reqProvince').value.trim(),
        start_date: startVal + 'T00:00:01',
        end_date: endVal + 'T23:59:59',
        budget_per_day: budget ? parseFloat(budget) : null,
    };

    try {
        await apiRequest('/requests', { method: 'POST', body: JSON.stringify(payload) });
        closeModal();
        showAlert('Demanda publicada correctamente', 'success');
        loadRequests();
    } catch (e) {
        showAlert('Error al publicar: ' + e.message, 'danger');
    }
}
