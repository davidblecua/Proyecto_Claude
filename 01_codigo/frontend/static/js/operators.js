/**
 * RentaMaq - Operarios
 * Gestion de operarios: listado publico, publicacion, reservas
 */

let currentOperatorsList = [];
let activeSkillFilter = '';
let currentOperatorView = 'machinery'; // 'machinery' | 'operators'

const OPERATOR_SKILL_LABELS = {
    'excavadora': 'Excavadora',
    'retroexcavadora': 'Retroexcavadora',
    'dumper': 'Dumper',
    'pala_cargadora': 'Pala Cargadora',
    'hormigonera': 'Hormigonera',
    'camion_grua': 'Camion Grua',
    'grua_torre': 'Grua Torre',
    'manipulador_telescopico': 'Manipulador Telescopico',
    'plataforma_elevadora': 'Plataforma Elevadora',
    'carretilla_elevadora': 'Carretilla Elevadora',
    'compactadora': 'Compactadora',
    'bulldozer': 'Bulldozer',
    'martillo_hidraulico': 'Martillo Hidraulico',
    'generador': 'Generador',
    'compresor': 'Compresor',
};

// ── Tabs de modo principal ────────────────────────────────────────────────────

function showMachineryTab() {
    currentOperatorView = 'machinery';
    document.getElementById('tabMachinery').classList.add('tab-active');
    document.getElementById('tabOperators').classList.remove('tab-active');
    document.getElementById('machinerySection').style.display = '';
    document.getElementById('operatorsSection').style.display = 'none';
    document.getElementById('permanentMapSection').style.display = '';
}

function showOperatorsTab() {
    currentOperatorView = 'operators';
    document.getElementById('tabOperators').classList.add('tab-active');
    document.getElementById('tabMachinery').classList.remove('tab-active');
    document.getElementById('machinerySection').style.display = 'none';
    document.getElementById('permanentMapSection').style.display = 'none';
    const section = document.getElementById('operatorsSection');
    section.style.display = '';

    // Renderizar busqueda si aun no esta
    if (!document.getElementById('operatorsSearchBox')) {
        renderOperatorsSearchBox();
    }
    if (currentOperatorsList.length === 0) {
        loadOperators();
    } else {
        renderOperators(currentOperatorsList);
    }
}

// ── Carga y renderizado ───────────────────────────────────────────────────────

async function loadOperators(skill, city, maxPrice) {
    const grid = document.getElementById('operatorsGrid');
    if (!grid) return;
    grid.innerHTML = '<div style="text-align:center;padding:2rem;"><div class="spinner"></div></div>';

    const params = new URLSearchParams({ limit: 50 });
    if (skill) params.set('skill', skill);
    if (city) params.set('city', city);
    if (maxPrice) params.set('max_price', maxPrice);

    try {
        const data = await apiRequest('/operators/search?' + params.toString());
        currentOperatorsList = data;
        activeSkillFilter = skill || '';
        renderOperators(data);
        renderOperatorFilterBar();
    } catch (e) {
        grid.innerHTML = '<p class="text-center" style="color:var(--danger-color);">Error al cargar operarios.</p>';
    }
}

function renderOperators(list) {
    const grid = document.getElementById('operatorsGrid');
    if (!grid) return;
    if (!list || list.length === 0) {
        grid.innerHTML = '<p class="text-center" style="color:var(--gray-600);padding:2rem;">No se encontraron operarios con estos filtros.</p>';
        return;
    }
    grid.innerHTML = '';
    list.forEach(op => grid.appendChild(createOperatorCard(op)));
}

function createOperatorCard(op) {
    const card = document.createElement('div');
    card.className = 'card operator-card';

    const skills = (op.machine_skills || []).map(s =>
        `<span class="badge badge-info skill-badge">${OPERATOR_SKILL_LABELS[s] || s}</span>`
    ).join('');
    const experience = op.experience_years != null ? `${op.experience_years} ano${op.experience_years !== 1 ? 's' : ''} exp.` : '';

    card.innerHTML = `
        <div class="operator-card-header">
            <div class="operator-avatar">${op.name.charAt(0).toUpperCase()}</div>
            <div class="operator-card-info">
                <h3 class="operator-name">${escHtml(op.name)}</h3>
                <p class="operator-location">
                    <span>Ubicacion:</span> ${escHtml(op.location_city)}, ${escHtml(op.location_province)}
                </p>
                ${experience ? `<p class="operator-exp">${experience}</p>` : ''}
            </div>
            <div class="operator-rate">
                <strong>${formatPrice(op.daily_rate)}</strong>
                <span>/dia</span>
            </div>
        </div>
        <div class="operator-skills">${skills || '<span style="color:var(--gray-500);font-size:0.82rem;">Sin especialidades indicadas</span>'}</div>
        ${op.description ? `<p class="operator-desc">${escHtml(op.description.substring(0, 120))}${op.description.length > 120 ? '...' : ''}</p>` : ''}
        <div class="operator-card-footer">
            ${op.is_available
                ? '<span class="badge badge-success">Disponible</span>'
                : '<span class="badge badge-warning">No disponible</span>'}
            <button class="btn btn-primary btn-sm" onclick="showOperatorModal(${op.id})">Ver y Reservar</button>
        </div>
    `;
    return card;
}

function escHtml(str) {
    return String(str || '')
        .replace(/&/g, '&amp;').replace(/</g, '&lt;')
        .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

// ── Busqueda de operarios ─────────────────────────────────────────────────────

function renderOperatorsSearchBox() {
    const section = document.getElementById('operatorsSection');
    if (!section) return;

    const skillOptions = Object.entries(OPERATOR_SKILL_LABELS).map(([v, l]) =>
        `<option value="${v}">${l}</option>`).join('');

    const box = document.createElement('div');
    box.className = 'search-box';
    box.id = 'operatorsSearchBox';
    box.innerHTML = `
        <h2 class="text-center mb-3">Busca el operario que necesitas</h2>
        <form class="search-form" id="operatorsSearchForm" onsubmit="searchOperators(event)">
            <div class="form-group">
                <label for="opSkill">Especialidad</label>
                <select class="form-control" id="opSkill">
                    <option value="">Todas</option>
                    ${skillOptions}
                </select>
            </div>
            <div class="form-group">
                <label for="opCity">Ciudad</label>
                <input type="text" class="form-control" id="opCity" placeholder="Madrid, Barcelona...">
            </div>
            <div class="form-group">
                <label for="opMaxPrice">Precio max/dia (euros)</label>
                <input type="number" class="form-control" id="opMaxPrice" placeholder="200">
            </div>
            <div class="form-group" style="align-self:flex-end;">
                <button type="submit" class="btn btn-primary" style="width:100%;">Buscar</button>
            </div>
        </form>
    `;
    section.insertBefore(box, section.firstChild);
}

async function searchOperators(event) {
    event.preventDefault();
    const skill = document.getElementById('opSkill').value;
    const city = document.getElementById('opCity').value;
    const maxPrice = document.getElementById('opMaxPrice').value;
    await loadOperators(skill || null, city || null, maxPrice || null);
}

// ── Barra de filtro por habilidad ────────────────────────────────────────────

function renderOperatorFilterBar() {
    const existing = document.getElementById('operatorFilterBar');
    if (existing) existing.remove();

    const grid = document.getElementById('operatorsGrid');
    const section = document.getElementById('operatorsSection');
    if (!grid || !section) return;

    const chipsHtml = [['', 'Todos'], ...Object.entries(OPERATOR_SKILL_LABELS)].map(([val, label]) =>
        `<button class="chip ${val === activeSkillFilter ? 'chip-active' : ''}"
                 data-skill="${val}"
                 onclick="applySkillFilter('${val}')">${label}</button>`
    ).join('');

    const bar = document.createElement('div');
    bar.id = 'operatorFilterBar';
    bar.className = 'public-filter-bar';
    bar.innerHTML = `
        <div class="filter-section">
            <span class="filter-section-label">Filtrar por especialidad</span>
            <div class="filter-chips" id="skillFilterChips">${chipsHtml}</div>
        </div>
    `;
    section.insertBefore(bar, grid);
}

function applySkillFilter(skill) {
    activeSkillFilter = skill;
    document.querySelectorAll('#skillFilterChips .chip').forEach(btn => {
        btn.classList.toggle('chip-active', btn.getAttribute('data-skill') === skill);
    });
    const filtered = skill
        ? currentOperatorsList.filter(op => (op.machine_skills || []).includes(skill))
        : currentOperatorsList;
    renderOperators(filtered);
}

// ── Modal de detalle del operario ─────────────────────────────────────────────

async function showOperatorModal(operatorId) {
    let op;
    try {
        op = await apiRequest('/operators/' + operatorId);
    } catch (e) {
        showAlert('Error al cargar el operario', 'danger');
        return;
    }

    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.id = 'operatorDetailModal';

    const skills = (op.machine_skills || []).map(s =>
        `<span class="badge badge-info skill-badge">${OPERATOR_SKILL_LABELS[s] || s}</span>`
    ).join('');

    const isOwner = appState.isAuthenticated && appState.currentUser.id === op.owner_id;

    const today = new Date().toISOString().split('T')[0];
    const next7 = new Date(); next7.setDate(next7.getDate() + 7);
    const next7str = next7.toISOString().split('T')[0];

    modal.innerHTML = `
        <div class="modal-dialog modal-lg">
            <div class="modal-header">
                <h3>${escHtml(op.name)}</h3>
                <button class="modal-close" onclick="closeOperatorModal()">x</button>
            </div>
            <div class="modal-body">
                <div class="operator-modal-top">
                    <div class="operator-avatar operator-avatar-lg">${op.name.charAt(0).toUpperCase()}</div>
                    <div style="flex:1;">
                        <div style="display:flex;gap:0.5rem;flex-wrap:wrap;margin-bottom:0.5rem;">
                            ${skills}
                            ${op.is_available
                                ? '<span class="badge badge-success">Disponible</span>'
                                : '<span class="badge badge-warning">No disponible</span>'}
                        </div>
                        <div class="detail-info-grid" style="margin-top:0.5rem;">
                            <div><span class="detail-label">Ubicacion</span><span>${escHtml(op.location_city)}, ${escHtml(op.location_province)}</span></div>
                            <div><span class="detail-label">Tarifa diaria</span><span><strong>${formatPrice(op.daily_rate)}</strong></span></div>
                            ${op.experience_years != null ? `<div><span class="detail-label">Experiencia</span><span>${op.experience_years} ano${op.experience_years !== 1 ? 's' : ''}</span></div>` : ''}
                            ${op.phone ? `<div><span class="detail-label">Telefono</span><span>${escHtml(op.phone)}</span></div>` : ''}
                        </div>
                    </div>
                </div>
                ${op.description ? `<p style="color:var(--gray-700);margin:1rem 0;">${escHtml(op.description)}</p>` : ''}

                ${isOwner ? `
                <div class="alert alert-info" style="margin-top:1rem;">
                    Eres el propietario de este perfil de operario.
                    <button class="btn btn-secondary btn-sm" style="margin-left:0.75rem;" onclick="closeOperatorModal();showMyOperators()">Gestionar mis operarios</button>
                </div>
                ` : appState.isAuthenticated && op.is_available ? `
                <div class="availability-section" id="opBookingSection_${op.id}" style="margin-top:1rem;">
                    <h4 style="margin-bottom:0.75rem;">Reservar operario</h4>
                    <div class="avail-date-row" style="flex-wrap:wrap;gap:0.75rem;">
                        <div class="form-group" style="flex:1;min-width:140px;margin:0;">
                            <label style="font-size:0.85rem;">Fecha inicio <span class="req">*</span></label>
                            <input type="date" class="form-control" id="opStart_${op.id}" min="${today}" value="${today}">
                        </div>
                        <div class="form-group" style="flex:1;min-width:140px;margin:0;">
                            <label style="font-size:0.85rem;">Fecha fin <span class="req">*</span></label>
                            <input type="date" class="form-control" id="opEnd_${op.id}" min="${today}" value="${next7str}">
                        </div>
                        <div class="form-group" style="flex:1;min-width:170px;margin:0;">
                            <label style="font-size:0.85rem;">Tipo de reserva</label>
                            <select class="form-control" id="opBookingType_${op.id}" onchange="toggleMachinerySelect(${op.id})">
                                <option value="operator_only">Solo operario</option>
                                <option value="machinery_with_operator">Operario + maquinaria mia</option>
                            </select>
                        </div>
                    </div>
                    <div id="opMachineryRow_${op.id}" style="margin-top:0.6rem;display:none;">
                        <div class="form-group" style="margin:0;">
                            <label style="font-size:0.85rem;">ID de maquinaria a usar (opcional)</label>
                            <input type="number" class="form-control" id="opMachineryId_${op.id}" placeholder="ID de tu maquinaria">
                        </div>
                    </div>
                    <div class="form-group" style="margin-top:0.6rem;">
                        <label style="font-size:0.85rem;">Notas adicionales</label>
                        <input type="text" class="form-control" id="opNotes_${op.id}" placeholder="Obra, condiciones especiales..." maxlength="500">
                    </div>
                    <div id="opCostPreview_${op.id}" style="margin-top:0.5rem;"></div>
                    <button class="btn btn-primary" style="margin-top:0.75rem;" onclick="submitOperatorBooking(${op.id}, ${op.daily_rate})">
                        Confirmar Reserva
                    </button>
                </div>` : !appState.isAuthenticated ? `
                <div class="alert alert-info" style="margin-top:1rem;">
                    <a href="#" onclick="closeOperatorModal();showLogin()">Inicia sesion</a> para reservar este operario.
                </div>` : `
                <div class="alert alert-warning" style="margin-top:1rem;">Este operario no esta disponible actualmente.</div>`}

                <div id="operatorReviews_${op.id}" style="margin-top:1.5rem;"></div>

                <div style="margin-top:1.5rem;">
                    <button class="btn btn-secondary" onclick="closeOperatorModal()">Cerrar</button>
                </div>
            </div>
        </div>
    `;

    document.body.appendChild(modal);
    modal.addEventListener('click', e => { if (e.target === modal) closeOperatorModal(); });
    loadReviews('operator', op.id, `operatorReviews_${op.id}`);

    // Mostrar preview de coste al cambiar fechas
    if (appState.isAuthenticated && op.is_available && !isOwner) {
        ['opStart_' + op.id, 'opEnd_' + op.id].forEach(id => {
            const el = document.getElementById(id);
            if (el) el.addEventListener('change', () => updateOpCostPreview(op.id, op.daily_rate));
        });
        updateOpCostPreview(op.id, op.daily_rate);
    }
}

function closeOperatorModal() {
    const modal = document.getElementById('operatorDetailModal');
    if (modal) modal.remove();
}

function toggleMachinerySelect(opId) {
    const select = document.getElementById('opBookingType_' + opId);
    const row = document.getElementById('opMachineryRow_' + opId);
    if (row) row.style.display = select && select.value === 'machinery_with_operator' ? '' : 'none';
}

function updateOpCostPreview(opId, dailyRate) {
    const startEl = document.getElementById('opStart_' + opId);
    const endEl = document.getElementById('opEnd_' + opId);
    const preview = document.getElementById('opCostPreview_' + opId);
    if (!startEl || !endEl || !preview) return;

    const start = new Date(startEl.value);
    const end = new Date(endEl.value);
    if (isNaN(start) || isNaN(end) || end <= start) {
        preview.innerHTML = '';
        return;
    }
    const days = Math.max(1, Math.round((end - start) / 86400000));
    const total = dailyRate * days;
    preview.innerHTML = `<span style="color:var(--success-color);font-weight:600;">${days} dia${days !== 1 ? 's' : ''} x ${formatPrice(dailyRate)} = ${formatPrice(total)}</span>`;
}

async function submitOperatorBooking(opId, dailyRate) {
    const startEl = document.getElementById('opStart_' + opId);
    const endEl = document.getElementById('opEnd_' + opId);
    const typeEl = document.getElementById('opBookingType_' + opId);
    const notesEl = document.getElementById('opNotes_' + opId);
    const machineEl = document.getElementById('opMachineryId_' + opId);

    if (!startEl || !endEl || !startEl.value || !endEl.value) {
        showAlert('Selecciona fechas de inicio y fin', 'danger');
        return;
    }
    if (endEl.value <= startEl.value) {
        showAlert('La fecha de fin debe ser posterior a la de inicio', 'danger');
        return;
    }

    const payload = {
        operator_id: opId,
        booking_type: typeEl ? typeEl.value : 'operator_only',
        start_date: startEl.value,
        end_date: endEl.value,
        notes: notesEl ? notesEl.value : null,
    };
    if (payload.booking_type === 'machinery_with_operator' && machineEl && machineEl.value) {
        payload.machinery_id = parseInt(machineEl.value);
    }

    const btn = document.querySelector('#opBookingSection_' + opId + ' .btn-primary');
    if (btn) { btn.disabled = true; btn.textContent = 'Procesando...'; }

    try {
        const result = await apiRequest('/operators/bookings', {
            method: 'POST',
            body: JSON.stringify(payload),
        });
        closeOperatorModal();
        showAlert(`Reserva confirmada! Total: ${formatPrice(result.total_cost)} por ${result.total_days} dia${result.total_days !== 1 ? 's' : ''}.`, 'success');
    } catch (e) {
        showAlert('Error al crear la reserva: ' + e.message, 'danger');
        if (btn) { btn.disabled = false; btn.textContent = 'Confirmar Reserva'; }
    }
}

// ── Mis Operarios (dashboard) ─────────────────────────────────────────────────

async function showMyOperators() {
    if (!appState.isAuthenticated) { showLogin(); return; }

    const mainContent = document.getElementById('mainContent');
    mainContent.innerHTML = `
        <div class="container mt-4">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:1rem;flex-wrap:wrap;gap:0.5rem;">
                <div>
                    <h2>Mis Operarios</h2>
                    <p style="color:var(--gray-600);margin:0;">Perfil de operarios que has publicado</p>
                </div>
                <div style="display:flex;gap:0.5rem;">
                    <button class="btn btn-secondary" onclick="showDashboard()">Panel</button>
                    <button class="btn btn-success" onclick="showPublishOperator()">+ Publicar Operario</button>
                </div>
            </div>
            <div id="myOperatorsGrid" class="card-grid"></div>
        </div>
    `;

    try {
        const data = await apiRequest('/operators/my/operators');
        const grid = document.getElementById('myOperatorsGrid');
        if (!data || data.length === 0) {
            grid.innerHTML = `
                <div style="grid-column:1/-1;text-align:center;padding:3rem;">
                    <div style="font-size:3rem;margin-bottom:1rem;"></div>
                    <h3>No has publicado ningun operario</h3>
                    <p style="color:var(--gray-600);margin-bottom:1rem;">Publica el perfil de un operario para que otros puedan contratarlo</p>
                    <button class="btn btn-success" onclick="showPublishOperator()">Publicar Operario</button>
                </div>`;
        } else {
            data.forEach(op => grid.appendChild(createMyOperatorCard(op)));
        }
    } catch (e) {
        showAlert('Error al cargar tus operarios', 'danger');
    }
}

function createMyOperatorCard(op) {
    const card = document.createElement('div');
    card.className = 'card operator-card';
    const skills = (op.machine_skills || []).map(s =>
        `<span class="badge badge-info skill-badge">${OPERATOR_SKILL_LABELS[s] || s}</span>`
    ).join('');
    card.innerHTML = `
        <div class="operator-card-header">
            <div class="operator-avatar">${op.name.charAt(0).toUpperCase()}</div>
            <div class="operator-card-info">
                <h3 class="operator-name">${escHtml(op.name)}</h3>
                <p class="operator-location">${escHtml(op.location_city)}, ${escHtml(op.location_province)}</p>
                <p style="font-weight:600;margin:0.2rem 0;">${formatPrice(op.daily_rate)}/dia</p>
            </div>
            <div>
                ${op.is_available
                    ? '<span class="badge badge-success">Disponible</span>'
                    : '<span class="badge badge-warning">No disponible</span>'}
            </div>
        </div>
        <div class="operator-skills">${skills}</div>
        <div class="operator-card-footer">
            <button class="btn btn-primary btn-sm" onclick="showEditOperatorModal(${op.id})">Editar</button>
            <button class="btn btn-danger btn-sm" onclick="deleteOperator(${op.id})">Eliminar</button>
        </div>
    `;
    return card;
}

async function deleteOperator(opId) {
    if (!confirm('Eliminar este operario del catalogo?')) return;
    try {
        await apiRequest('/operators/' + opId, { method: 'DELETE' });
        showAlert('Operario eliminado', 'success');
        showMyOperators();
    } catch (e) {
        showAlert('Error al eliminar: ' + e.message, 'danger');
    }
}

// ── Publicar operario ─────────────────────────────────────────────────────────

function showPublishOperator() {
    if (!appState.isAuthenticated) { showLogin(); return; }

    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.id = 'publishOperatorModal';

    const skillCheckboxes = Object.entries(OPERATOR_SKILL_LABELS).map(([v, l]) =>
        `<label class="skill-checkbox-label">
            <input type="checkbox" name="opSkillCheck" value="${v}"> ${l}
        </label>`
    ).join('');

    modal.innerHTML = `
        <div class="modal-dialog modal-lg">
            <div class="modal-header">
                <h3>Publicar Operario</h3>
                <button class="modal-close" onclick="document.getElementById('publishOperatorModal').remove()">x</button>
            </div>
            <div class="modal-body">
                <form id="publishOperatorForm" onsubmit="submitPublishOperator(event)">
                    <div class="form-row-2">
                        <div class="form-group">
                            <label>Nombre completo <span class="req">*</span></label>
                            <input type="text" class="form-control" id="opName" required minlength="2" maxlength="255">
                        </div>
                        <div class="form-group">
                            <label>Telefono</label>
                            <input type="text" class="form-control" id="opPhone" maxlength="20">
                        </div>
                    </div>
                    <div class="form-group">
                        <label>Descripcion / Experiencia</label>
                        <textarea class="form-control" id="opDescription" rows="3" maxlength="2000" placeholder="Describe la experiencia, certificaciones, disponibilidad..."></textarea>
                    </div>
                    <div class="form-row-3">
                        <div class="form-group">
                            <label>Tarifa diaria (euros) <span class="req">*</span></label>
                            <input type="number" class="form-control" id="opDailyRate" required min="1" step="0.01">
                        </div>
                        <div class="form-group">
                            <label>Anos de experiencia</label>
                            <input type="number" class="form-control" id="opExpYears" min="0" max="60">
                        </div>
                        <div class="form-group">
                            <label>Disponible</label>
                            <select class="form-control" id="opIsAvailable">
                                <option value="true">Si</option>
                                <option value="false">No</option>
                            </select>
                        </div>
                    </div>
                    <div class="form-row-2">
                        <div class="form-group">
                            <label>Ciudad <span class="req">*</span></label>
                            <input type="text" class="form-control" id="opCityPub" required maxlength="100">
                        </div>
                        <div class="form-group">
                            <label>Provincia <span class="req">*</span></label>
                            <input type="text" class="form-control" id="opProvince" required maxlength="100">
                        </div>
                    </div>
                    <div class="form-group">
                        <label>Maquinaria que puede manejar <span class="req">*</span></label>
                        <div class="skill-checkboxes-grid">${skillCheckboxes}</div>
                    </div>
                    <div style="display:flex;gap:0.75rem;margin-top:1rem;">
                        <button type="submit" class="btn btn-success">Publicar Operario</button>
                        <button type="button" class="btn btn-secondary" onclick="document.getElementById('publishOperatorModal').remove()">Cancelar</button>
                    </div>
                </form>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
    modal.addEventListener('click', e => { if (e.target === modal) modal.remove(); });
}

async function submitPublishOperator(event) {
    event.preventDefault();

    const skills = Array.from(document.querySelectorAll('input[name="opSkillCheck"]:checked')).map(el => el.value);
    if (skills.length === 0) {
        showAlert('Selecciona al menos una especialidad de maquinaria', 'danger');
        return;
    }

    const payload = {
        name: document.getElementById('opName').value.trim(),
        description: document.getElementById('opDescription').value.trim() || null,
        daily_rate: parseFloat(document.getElementById('opDailyRate').value),
        experience_years: document.getElementById('opExpYears').value ? parseInt(document.getElementById('opExpYears').value) : null,
        phone: document.getElementById('opPhone').value.trim() || null,
        location_city: document.getElementById('opCityPub').value.trim(),
        location_province: document.getElementById('opProvince').value.trim(),
        is_available: document.getElementById('opIsAvailable').value === 'true',
        machine_skills: skills,
    };

    const btn = document.querySelector('#publishOperatorForm .btn-success');
    if (btn) { btn.disabled = true; btn.textContent = 'Publicando...'; }

    try {
        await apiRequest('/operators', { method: 'POST', body: JSON.stringify(payload) });
        document.getElementById('publishOperatorModal').remove();
        showAlert('Operario publicado correctamente', 'success');
        // Recargar la lista de mis operarios si estamos en esa vista
        if (document.getElementById('myOperatorsGrid')) showMyOperators();
    } catch (e) {
        showAlert('Error al publicar: ' + e.message, 'danger');
        if (btn) { btn.disabled = false; btn.textContent = 'Publicar Operario'; }
    }
}

// ── Editar operario ───────────────────────────────────────────────────────────

async function showEditOperatorModal(opId) {
    let op;
    try {
        op = await apiRequest('/operators/' + opId);
    } catch (e) {
        showAlert('Error al cargar el operario', 'danger');
        return;
    }

    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.id = 'editOperatorModal';

    const skillCheckboxes = Object.entries(OPERATOR_SKILL_LABELS).map(([v, l]) =>
        `<label class="skill-checkbox-label">
            <input type="checkbox" name="editOpSkillCheck" value="${v}" ${(op.machine_skills || []).includes(v) ? 'checked' : ''}> ${l}
        </label>`
    ).join('');

    modal.innerHTML = `
        <div class="modal-dialog modal-lg">
            <div class="modal-header">
                <h3>Editar Operario</h3>
                <button class="modal-close" onclick="document.getElementById('editOperatorModal').remove()">x</button>
            </div>
            <div class="modal-body">
                <form id="editOperatorForm" onsubmit="submitEditOperator(event, ${opId})">
                    <div class="form-row-2">
                        <div class="form-group">
                            <label>Nombre <span class="req">*</span></label>
                            <input type="text" class="form-control" id="editOpName" value="${escHtml(op.name)}" required minlength="2">
                        </div>
                        <div class="form-group">
                            <label>Telefono</label>
                            <input type="text" class="form-control" id="editOpPhone" value="${escHtml(op.phone || '')}">
                        </div>
                    </div>
                    <div class="form-group">
                        <label>Descripcion</label>
                        <textarea class="form-control" id="editOpDesc" rows="3">${escHtml(op.description || '')}</textarea>
                    </div>
                    <div class="form-row-3">
                        <div class="form-group">
                            <label>Tarifa diaria (euros) <span class="req">*</span></label>
                            <input type="number" class="form-control" id="editOpRate" value="${op.daily_rate}" required min="1" step="0.01">
                        </div>
                        <div class="form-group">
                            <label>Anos de experiencia</label>
                            <input type="number" class="form-control" id="editOpExp" value="${op.experience_years != null ? op.experience_years : ''}" min="0" max="60">
                        </div>
                        <div class="form-group">
                            <label>Disponible</label>
                            <select class="form-control" id="editOpAvail">
                                <option value="true" ${op.is_available ? 'selected' : ''}>Si</option>
                                <option value="false" ${!op.is_available ? 'selected' : ''}>No</option>
                            </select>
                        </div>
                    </div>
                    <div class="form-row-2">
                        <div class="form-group">
                            <label>Ciudad <span class="req">*</span></label>
                            <input type="text" class="form-control" id="editOpCity" value="${escHtml(op.location_city)}" required>
                        </div>
                        <div class="form-group">
                            <label>Provincia <span class="req">*</span></label>
                            <input type="text" class="form-control" id="editOpProv" value="${escHtml(op.location_province)}" required>
                        </div>
                    </div>
                    <div class="form-group">
                        <label>Especialidades</label>
                        <div class="skill-checkboxes-grid">${skillCheckboxes}</div>
                    </div>
                    <div style="display:flex;gap:0.75rem;margin-top:1rem;">
                        <button type="submit" class="btn btn-primary">Guardar Cambios</button>
                        <button type="button" class="btn btn-secondary" onclick="document.getElementById('editOperatorModal').remove()">Cancelar</button>
                    </div>
                </form>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
    modal.addEventListener('click', e => { if (e.target === modal) modal.remove(); });
}

async function submitEditOperator(event, opId) {
    event.preventDefault();
    const skills = Array.from(document.querySelectorAll('input[name="editOpSkillCheck"]:checked')).map(el => el.value);

    const payload = {
        name: document.getElementById('editOpName').value.trim(),
        description: document.getElementById('editOpDesc').value.trim() || null,
        daily_rate: parseFloat(document.getElementById('editOpRate').value),
        experience_years: document.getElementById('editOpExp').value ? parseInt(document.getElementById('editOpExp').value) : null,
        phone: document.getElementById('editOpPhone').value.trim() || null,
        location_city: document.getElementById('editOpCity').value.trim(),
        location_province: document.getElementById('editOpProv').value.trim(),
        is_available: document.getElementById('editOpAvail').value === 'true',
        machine_skills: skills,
    };

    const btn = document.querySelector('#editOperatorForm .btn-primary');
    if (btn) { btn.disabled = true; btn.textContent = 'Guardando...'; }

    try {
        await apiRequest('/operators/' + opId, { method: 'PUT', body: JSON.stringify(payload) });
        document.getElementById('editOperatorModal').remove();
        showAlert('Operario actualizado correctamente', 'success');
        showMyOperators();
    } catch (e) {
        showAlert('Error al actualizar: ' + e.message, 'danger');
        if (btn) { btn.disabled = false; btn.textContent = 'Guardar Cambios'; }
    }
}

// ── Mis reservas de operarios ─────────────────────────────────────────────────

async function showMyOperatorBookings() {
    const container = document.getElementById('opBookingsContainer');
    if (!container) return;
    container.innerHTML = '<div class="spinner" style="margin:1rem auto;"></div>';
    try {
        const data = await apiRequest('/operators/bookings/my');
        if (!data || data.length === 0) {
            container.innerHTML = '<p style="color:var(--gray-600);">No tienes reservas de operarios todavia.</p>';
            return;
        }
        container.innerHTML = data.map(b => `
            <div class="booking-card" style="margin-bottom:0.75rem;padding:1rem;border:1px solid var(--gray-200);border-radius:var(--border-radius);">
                <div style="display:flex;justify-content:space-between;flex-wrap:wrap;gap:0.5rem;">
                    <div>
                        <strong>${escHtml(b.operator_name)}</strong>
                        <span class="badge badge-info" style="margin-left:0.5rem;">${b.booking_type === 'operator_only' ? 'Solo operario' : 'Operario + Maquinaria'}</span>
                    </div>
                    <span class="badge badge-${b.status === 'pending' ? 'warning' : b.status === 'confirmed' ? 'success' : 'secondary'}">${b.status}</span>
                </div>
                <div style="margin-top:0.4rem;font-size:0.88rem;color:var(--gray-700);">
                    ${formatDate(b.start_date)} - ${formatDate(b.end_date)} &middot; ${b.total_days} dia${b.total_days !== 1 ? 's' : ''}
                </div>
                ${b.machinery_title ? `<div style="font-size:0.85rem;color:var(--gray-600);">Maquinaria: ${escHtml(b.machinery_title)}</div>` : ''}
                <div style="font-weight:600;margin-top:0.3rem;">Total: ${formatPrice(b.total_cost)}</div>
                ${b.notes ? `<div style="font-size:0.82rem;color:var(--gray-600);margin-top:0.2rem;">${escHtml(b.notes)}</div>` : ''}
            </div>
        `).join('');
    } catch (e) {
        container.innerHTML = '<p style="color:var(--danger-color);">Error al cargar reservas de operarios.</p>';
    }
}
