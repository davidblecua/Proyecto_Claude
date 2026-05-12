/**
 * RentaMaq - Búsqueda y Reservas
 * Funcionalidad de búsqueda y gestión de reservas
 */

/**
 * Busca maquinaria con filtros
 */
async function searchMachinery(event) {
    event.preventDefault();
    
    const machineryType = document.getElementById('machineryType').value;
    const locationCity = document.getElementById('locationCity').value;
    const maxPrice = document.getElementById('maxPrice').value;
    
    const params = new URLSearchParams();
    if (machineryType) params.append('machinery_type', machineryType);
    if (locationCity) params.append('location_city', locationCity);
    if (maxPrice) params.append('max_price', maxPrice);
    params.append('limit', '20');
    
    const grid = document.getElementById('machineryGrid');
    const spinner = document.getElementById('loadingSpinner');
    
    try {
        spinner.style.display = 'block';
        grid.innerHTML = '';
        
        const data = await apiRequest(`/machinery/search?${params.toString()}`);
        
        if (data.machinery && data.machinery.length > 0) {
            currentMachineryList = data.machinery;
            activeTypeFilter = '';
            dateFilterActive = false;
            renderMachinery(data.machinery);
            renderFilterBar();
            showAlert(`Se encontraron ${data.total} resultados`, 'success');
        } else {
            grid.innerHTML = '<p class="text-center">No se encontró maquinaria con estos filtros.</p>';
        }
    } catch (error) {
        console.error('Error en búsqueda:', error);
        showAlert('Error al buscar maquinaria', 'danger');
    } finally {
        spinner.style.display = 'none';
    }
}

/**
 * Muestra la maquinaria del usuario actual con gestión completa
 */
async function showMyMachinery() {
    if (!appState.isAuthenticated) {
        showLogin();
        return;
    }

    const mainContent = document.getElementById('mainContent');
    mainContent.innerHTML = `
        <div class="container mt-4">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:1rem;">
                <div>
                    <h2>Gestionar Mi Maquinaria</h2>
                    <p style="color:var(--gray-600);margin:0;">Edita, actualiza y gestiona tu inventario</p>
                </div>
                <div style="display:flex;gap:0.5rem;">
                    <button class="btn btn-secondary" onclick="showDashboard()">← Panel</button>
                    <button class="btn btn-success" onclick="showAddMachinery()">+ Nueva Máquina</button>
                </div>
            </div>
            <div id="myMachineryGrid" class="card-grid"></div>
            <div id="loadingMyMachinery" style="display:none;text-align:center;padding:2rem;">
                <div class="spinner"></div>
            </div>
        </div>
    `;

    try {
        document.getElementById('loadingMyMachinery').style.display = 'block';
        const data = await apiRequest(`/machinery/my/machinery`);
        const grid = document.getElementById('myMachineryGrid');

        if (data && data.length > 0) {
            data.forEach(machinery => grid.appendChild(createMyMachineryCard(machinery)));
        } else {
            grid.innerHTML = `
                <div style="grid-column:1/-1;text-align:center;padding:3rem;">
                    <h3>No has publicado ninguna máquina aún</h3>
                    <p style="color:var(--gray-600);margin-bottom:1rem;">Empieza añadiendo tu primera máquina al catálogo</p>
                    <button class="btn btn-success" onclick="showAddMachinery()">Publicar Primera Máquina</button>
                </div>`;
        }
    } catch (error) {
        showAlert('Error al cargar tus máquinas', 'danger');
    } finally {
        if (document.getElementById('loadingMyMachinery'))
            document.getElementById('loadingMyMachinery').style.display = 'none';
    }
}

/**
 * Crea una tarjeta de maquinaria propia con opciones completas
 */
function createMyMachineryCard(machinery) {
    const card = document.createElement('div');
    card.className = 'card manage-machinery-card';

    const images = machinery.images && machinery.images.length > 0 ? machinery.images : [];
    const imgUrl = images[0] || 'https://via.placeholder.com/300x180?text=Sin+Imagen';
    const extraPhotos = images.length > 1 ? `<span class="photo-count">+${images.length - 1} fotos</span>` : '';
    const availBadge = machinery.is_available
        ? '<span class="badge badge-success">Disponible</span>'
        : '<span class="badge badge-warning">No disponible</span>';

    card.innerHTML = `
        <div class="manage-card-img-wrap">
            <img src="${imgUrl}" alt="${machinery.title}" class="manage-card-img"
                 onerror="this.src='https://via.placeholder.com/300x180?text=Sin+Imagen'">
            ${extraPhotos}
            <div class="manage-card-status">${availBadge}</div>
        </div>
        <div class="card-body">
            <h4 class="card-title">${machinery.title}</h4>
            <p style="margin:0.25rem 0;"><span class="badge badge-info">${translateMachineryType(machinery.machinery_type)}</span></p>
            <p style="font-size:0.85rem;color:var(--gray-600);margin:0.25rem 0;">${machinery.location_city}, ${machinery.location_province}</p>
            <p style="font-weight:600;margin:0.5rem 0;">${formatPrice(machinery.daily_rate)}/día</p>
            <div class="manage-card-actions">
                <button class="btn btn-primary btn-sm" onclick="showEditMachineryModal(${machinery.id})">Editar</button>
                <button class="btn btn-secondary btn-sm" onclick="showBlockDatesModal(${machinery.id}, '${machinery.title.replace(/'/g, "\\'")}')">Bloquear Fechas</button>
                <button class="btn btn-danger btn-sm" onclick="deleteMachinery(${machinery.id})">Eliminar</button>
            </div>
        </div>
    `;
    return card;
}

/**
 * Abre el modal para editar una máquina
 */
async function showEditMachineryModal(machineryId) {
    let machinery;
    try {
        machinery = await apiRequest(`/machinery/${machineryId}`);
    } catch (e) {
        showAlert('Error al cargar la máquina', 'danger');
        return;
    }

    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.id = 'editMachineryModal';
    modal.innerHTML = `
        <div class="modal-dialog modal-lg">
            <div class="modal-header">
                <h3>Editar Maquinaria</h3>
                <button class="modal-close" onclick="document.getElementById('editMachineryModal').remove()">&times;</button>
            </div>
            <div class="modal-body">
                <form id="editMachineryForm" onsubmit="handleEditMachinery(event, ${machineryId})">
                    <div class="form-row-2">
                        <div class="form-group">
                            <label>Título <span class="req">*</span></label>
                            <input type="text" class="form-control" id="editTitle" value="${escHtml(machinery.title)}" required minlength="5">
                        </div>
                        <div class="form-group">
                            <label>Tipo <span class="req">*</span></label>
                            <select class="form-control" id="editType" required>
                                ${buildMachineryTypeOptions(machinery.machinery_type)}
                            </select>
                        </div>
                    </div>
                    <div class="form-group">
                        <label>Descripción <span class="req">*</span></label>
                        <textarea class="form-control" id="editDescription" rows="3" required minlength="20">${escHtml(machinery.description)}</textarea>
                    </div>
                    <div class="form-row-3">
                        <div class="form-group">
                            <label>Marca</label>
                            <input type="text" class="form-control" id="editBrand" value="${escHtml(machinery.brand || '')}">
                        </div>
                        <div class="form-group">
                            <label>Modelo</label>
                            <input type="text" class="form-control" id="editModel" value="${escHtml(machinery.model || '')}">
                        </div>
                        <div class="form-group">
                            <label>Año</label>
                            <input type="number" class="form-control" id="editYear" value="${machinery.year || ''}" min="1990" max="2030">
                        </div>
                    </div>
                    <div class="form-row-3">
                        <div class="form-group">
                            <label>Precio diario (€) <span class="req">*</span></label>
                            <input type="number" class="form-control" id="editDailyRate" value="${machinery.daily_rate}" required step="0.01" min="1">
                        </div>
                        <div class="form-group">
                            <label>Ciudad <span class="req">*</span></label>
                            <input type="text" class="form-control" id="editCity" value="${escHtml(machinery.location_city)}" required>
                        </div>
                        <div class="form-group">
                            <label>Provincia <span class="req">*</span></label>
                            <input type="text" class="form-control" id="editProvince" value="${escHtml(machinery.location_province)}" required>
                        </div>
                    </div>
                    <div class="form-row-2">
                        <div class="form-group">
                            <label><input type="checkbox" id="editAvailable" ${machinery.is_available ? 'checked' : ''}> Disponible para alquiler</label>
                        </div>
                        <div class="form-group">
                            <label><input type="checkbox" id="editDelivery" ${machinery.delivery_available ? 'checked' : ''}> Entrega disponible</label>
                        </div>
                    </div>
                    <div class="form-group">
                        <label>Fotos de la máquina</label>
                        <div id="editExistingPhotos" class="photo-preview-grid">
                            ${(machinery.images || []).map((url, i) => `
                                <div class="photo-thumb-wrap" id="editThumb_${i}">
                                    <img src="${escHtml(url)}" class="photo-thumb" onerror="this.src='https://via.placeholder.com/100x75?text=Foto'">
                                    ${i === 0 ? '<span class="photo-cover-badge">Portada</span>' : ''}
                                    <button type="button" class="photo-thumb-del" onclick="removeExistingPhoto('${escHtml(url)}', 'editThumb_${i}')" title="Eliminar">×</button>
                                </div>`).join('')}
                        </div>
                        <div id="editAddPhotoArea" class="photo-upload-area photo-upload-area-sm" style="margin-top:0.5rem;"
                             onclick="document.getElementById('editNewPhotos').click()">
                            <input type="file" id="editNewPhotos" accept="image/jpeg,image/png,image/webp" multiple style="display:none"
                                   onchange="handlePhotoSelect(this, 'editNewPreviewGrid', 'editAddPhotoHint')">
                            <div id="editAddPhotoHint" class="photo-upload-hint" style="padding:0.5rem;">
                                <span>+ Añadir más fotos</span>
                                <small>JPG, PNG o WebP · máx. 5 MB</small>
                            </div>
                        </div>
                        <div id="editNewPreviewGrid" class="photo-preview-grid"></div>
                    </div>
                    <div style="display:flex;gap:0.5rem;justify-content:flex-end;margin-top:1rem;">
                        <button type="button" class="btn btn-secondary" onclick="document.getElementById('editMachineryModal').remove()">Cancelar</button>
                        <button type="submit" class="btn btn-primary">Guardar Cambios</button>
                    </div>
                </form>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
    modal.addEventListener('click', e => { if (e.target === modal) modal.remove(); });
    document.getElementById('editNewPreviewGrid').addEventListener('click', e => e.stopPropagation());
    // Guardar URLs a borrar
    modal._photosToDelete = [];
    window._editPhotosToDelete = [];
    window._editPendingFiles = [];
}

async function handleEditMachinery(event, machineryId) {
    event.preventDefault();
    const data = {
        title: document.getElementById('editTitle').value,
        description: document.getElementById('editDescription').value,
        daily_rate: parseFloat(document.getElementById('editDailyRate').value),
        location_city: document.getElementById('editCity').value,
        location_province: document.getElementById('editProvince').value,
        is_available: document.getElementById('editAvailable').checked,
        delivery_available: document.getElementById('editDelivery').checked
    };
    try {
        await apiRequest(`/machinery/${machineryId}`, { method: 'PUT', body: JSON.stringify(data) });

        // Eliminar fotos marcadas para borrar
        if (window._editPhotosToDelete && window._editPhotosToDelete.length > 0) {
            await apiRequest(`/machinery/${machineryId}/photos`, {
                method: 'DELETE',
                body: JSON.stringify({ urls: window._editPhotosToDelete })
            });
        }

        // Subir fotos nuevas
        if (window._editPendingFiles && window._editPendingFiles.length > 0) {
            await uploadPhotos(machineryId, window._editPendingFiles);
        }

        window._editPhotosToDelete = [];
        window._editPendingFiles = [];
        document.getElementById('editMachineryModal').remove();
        showAlert('Máquina actualizada correctamente', 'success');
        showMyMachinery();
    } catch (e) {
        showAlert('Error al actualizar: ' + e.message, 'danger');
    }
}

/**
 * Abre el modal para bloquear fechas de una máquina
 */
function showBlockDatesModal(machineryId, machineryTitle) {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.id = 'blockDatesModal';
    modal.innerHTML = `
        <div class="modal-dialog">
            <div class="modal-header">
                <h3>Bloquear Fechas</h3>
                <button class="modal-close" onclick="document.getElementById('blockDatesModal').remove()">&times;</button>
            </div>
            <div class="modal-body">
                <p style="color:var(--gray-600);margin-bottom:1rem;">${escHtml(machineryTitle)}</p>
                <form id="blockDatesForm" onsubmit="handleBlockDates(event, ${machineryId})">
                    <div class="form-row-2">
                        <div class="form-group">
                            <label>Fecha inicio <span class="req">*</span></label>
                            <input type="date" class="form-control" id="blockStart" required>
                        </div>
                        <div class="form-group">
                            <label>Fecha fin <span class="req">*</span></label>
                            <input type="date" class="form-control" id="blockEnd" required>
                        </div>
                    </div>
                    <div class="form-group">
                        <label>Razón <span class="req">*</span></label>
                        <select class="form-control" id="blockReason">
                            <option value="maintenance">Mantenimiento</option>
                            <option value="booked">Reservado externamente</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Notas (opcional)</label>
                        <input type="text" class="form-control" id="blockNotes" placeholder="Ej: Revisión anual">
                    </div>
                    <div style="display:flex;gap:0.5rem;justify-content:flex-end;margin-top:1rem;">
                        <button type="button" class="btn btn-secondary" onclick="document.getElementById('blockDatesModal').remove()">Cancelar</button>
                        <button type="submit" class="btn btn-primary">Bloquear Fechas</button>
                    </div>
                </form>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
    // Set min date to today
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('blockStart').min = today;
    document.getElementById('blockEnd').min = today;
    modal.addEventListener('click', e => { if (e.target === modal) modal.remove(); });
}

async function handleBlockDates(event, machineryId) {
    event.preventDefault();
    const start = document.getElementById('blockStart').value;
    const end = document.getElementById('blockEnd').value;
    const reason = document.getElementById('blockReason').value;
    const notes = document.getElementById('blockNotes').value;

    if (end < start) {
        showAlert('La fecha de fin debe ser posterior a la de inicio', 'danger');
        return;
    }
    try {
        await apiRequest(`/machinery/${machineryId}/blocks`, {
            method: 'POST',
            body: JSON.stringify({ start_date: start, end_date: end, reason, notes: notes || null })
        });
        document.getElementById('blockDatesModal').remove();
        showAlert('Fechas bloqueadas correctamente', 'success');
    } catch (e) {
        showAlert('Error al bloquear fechas: ' + e.message, 'danger');
    }
}

// Helpers
function escHtml(str) {
    if (!str) return '';
    return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

// ── Gestión de fotos ──────────────────────────────────────────────────────────

/** Ficheros pendientes de subida en el formulario de nueva máquina */
let _pendingFiles = [];

/**
 * Maneja la selección de ficheros en un <input type="file">.
 * previewGridId: id del contenedor de miniaturas.
 * hintId: id del hint de la zona de drop (se oculta cuando hay fotos).
 */
function handlePhotoSelect(input, previewGridId, hintId) {
    const MAX = 10;
    const MAX_BYTES = 5 * 1024 * 1024;
    const ALLOWED = ['image/jpeg', 'image/png', 'image/webp'];
    const isEdit = previewGridId === 'editNewPreviewGrid';

    const files = Array.from(input.files);
    const target = isEdit ? '_editPendingFiles' : null;
    const existing = isEdit ? (window._editPendingFiles || []) : _pendingFiles;

    // Contar fotos ya existentes en DB (para edición)
    const dbCount = isEdit
        ? document.querySelectorAll('#editExistingPhotos .photo-thumb-wrap:not(.removed)').length
        : 0;

    const errEl = document.getElementById(isEdit ? null : 'photoError');
    const totalAfter = dbCount + existing.length + files.length;

    if (totalAfter > MAX) {
        if (errEl) { errEl.textContent = t('photos_max_reached'); errEl.style.display = 'block'; }
        input.value = '';
        return;
    }
    if (errEl) errEl.style.display = 'none';

    const grid = document.getElementById(previewGridId);
    const hint = document.getElementById(hintId);

    files.forEach(file => {
        if (!ALLOWED.includes(file.type)) {
            showAlert(`Formato no permitido: ${file.name}. Usa JPG, PNG o WebP.`, 'danger');
            return;
        }
        if (file.size > MAX_BYTES) {
            showAlert(`${file.name} supera el máximo de 5 MB.`, 'danger');
            return;
        }

        if (isEdit) {
            window._editPendingFiles = window._editPendingFiles || [];
            window._editPendingFiles.push(file);
        } else {
            _pendingFiles.push(file);
        }

        const idx = isEdit
            ? (window._editPendingFiles.length - 1)
            : (_pendingFiles.length - 1);

        const wrap = document.createElement('div');
        wrap.className = 'photo-thumb-wrap';
        wrap.id = `newThumb_${previewGridId}_${idx}`;

        const img = document.createElement('img');
        img.className = 'photo-thumb';
        const reader = new FileReader();
        reader.onload = e => { img.src = e.target.result; };
        reader.readAsDataURL(file);

        const isCover = !isEdit && _pendingFiles.length === 1 && dbCount === 0;
        const badge = isCover ? '<span class="photo-cover-badge">Portada</span>' : '';

        const del = document.createElement('button');
        del.type = 'button';
        del.className = 'photo-thumb-del';
        del.title = 'Eliminar';
        del.textContent = '×';
        del.onclick = () => {
            wrap.remove();
            if (isEdit) {
                window._editPendingFiles.splice(idx, 1);
            } else {
                _pendingFiles.splice(idx, 1);
            }
            refreshCoverBadge(previewGridId, dbCount);
        };

        wrap.appendChild(img);
        if (badge) wrap.insertAdjacentHTML('beforeend', badge);
        wrap.appendChild(del);
        grid.appendChild(wrap);
    });

    if (hint) hint.style.display = 'none';
    refreshCoverBadge(previewGridId, dbCount);
    input.value = '';  // reset para permitir seleccionar el mismo fichero otra vez
}

/** Actualiza el badge "Portada" para que siempre esté en el primer thumb. */
function refreshCoverBadge(previewGridId, existingDbCount) {
    const grid = document.getElementById(previewGridId);
    if (!grid) return;
    grid.querySelectorAll('.photo-cover-badge').forEach(b => b.remove());
    if (existingDbCount === 0) {
        const first = grid.querySelector('.photo-thumb-wrap');
        if (first) first.insertAdjacentHTML('afterbegin', '<span class="photo-cover-badge">Portada</span>');
    }
}

/** Marca una foto existente (en edición) para ser eliminada al guardar. */
function removeExistingPhoto(url, thumbId) {
    window._editPhotosToDelete = window._editPhotosToDelete || [];
    window._editPhotosToDelete.push(url);
    const el = document.getElementById(thumbId);
    if (el) { el.classList.add('removed'); el.style.display = 'none'; }
    // Si era la portada, actualizar badge en el siguiente thumb
    const remaining = document.querySelectorAll('#editExistingPhotos .photo-thumb-wrap:not(.removed)');
    document.querySelectorAll('#editExistingPhotos .photo-cover-badge').forEach(b => b.remove());
    if (remaining.length > 0) {
        remaining[0].insertAdjacentHTML('afterbegin', '<span class="photo-cover-badge">Portada</span>');
    }
}

/** Sube un array de File al endpoint de fotos de una máquina. */
async function uploadPhotos(machineryId, files) {
    if (!files || files.length === 0) return;
    const fd = new FormData();
    files.forEach(f => fd.append('files', f));
    const token = localStorage.getItem('access_token');
    const resp = await fetch(`/api/v1/machinery/${machineryId}/photos`, {
        method: 'POST',
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        body: fd
    });
    if (!resp.ok) {
        const err = await resp.json().catch(() => ({}));
        throw new Error(err.detail || 'Error al subir las fotos');
    }
    return resp.json();
}

function buildMachineryTypeOptions(selected) {
    const types = [
        ['excavadora','Excavadora'],['retroexcavadora','Retroexcavadora'],
        ['bulldozer','Bulldozer'],['motoniveladora','Motoniveladora'],
        ['pala_cargadora','Pala Cargadora'],['dumper','Dumper'],
        ['manipulador_telescopico','Manipulador Telescópico'],['carretilla_elevadora','Carretilla Elevadora'],
        ['montacargas','Montacargas'],['compactadora','Compactadora'],
        ['grua_torre','Grúa Torre'],['camion_grua','Camión Grúa'],
        ['plataforma_elevadora','Plataforma Elevadora'],['hormigonera','Hormigonera'],
        ['bomba_hormigon','Bomba de Hormigón'],['martillo_hidraulico','Martillo Hidráulico'],
        ['cortadora_asfalto','Cortadora de Asfalto'],['compresor','Compresor'],
        ['generador','Generador'],['andamio','Andamio']
    ];
    return types.map(([val, label]) =>
        `<option value="${val}" ${val === selected ? 'selected' : ''}>${label}</option>`
    ).join('');
}

/**
 * Cambia la disponibilidad de una máquina
 */
async function toggleAvailability(machineryId, isAvailable) {
    try {
        await apiRequest(`/machinery/${machineryId}/availability?is_available=${isAvailable}`, {
            method: 'PATCH'
        });
        
        showAlert('Disponibilidad actualizada', 'success');
        showMyMachinery(); // Recargar
    } catch (error) {
        showAlert('Error al actualizar disponibilidad', 'danger');
    }
}

/**
 * Elimina una máquina
 */
async function deleteMachinery(machineryId) {
    if (!confirm('¿Estás seguro de que deseas eliminar esta máquina?')) {
        return;
    }
    
    try {
        await apiRequest(`/machinery/${machineryId}`, {
            method: 'DELETE'
        });
        
        showAlert('Máquina eliminada correctamente', 'success');
        showMyMachinery(); // Recargar
    } catch (error) {
        showAlert('Error al eliminar la máquina', 'danger');
    }
}

/**
 * Muestra el formulario para agregar maquinaria
 */
function showAddMachinery() {
    const mainContent = document.getElementById('mainContent');
    
    mainContent.innerHTML = `
        <div class="container mt-4">
            <h2>Publicar Nueva Máquina</h2>
            <form id="addMachineryForm" onsubmit="handleAddMachinery(event)" style="max-width: 800px;">
                <div class="form-group">
                    <label>Título <span class="req">*</span></label>
                    <input type="text" class="form-control" id="machTitle" required>
                </div>

                <div class="form-group">
                    <label>Descripción <span class="req">*</span></label>
                    <textarea class="form-control" id="machDescription" rows="4" required></textarea>
                </div>

                <div class="form-group">
                    <label>Tipo de Maquinaria <span class="req">*</span></label>
                    <select class="form-control" id="machType" required>
                        ${buildMachineryTypeOptions('')}
                    </select>
                </div>
                
                <div class="form-group">
                    <label>Marca</label>
                    <input type="text" class="form-control" id="machBrand">
                </div>
                
                <div class="form-group">
                    <label>Modelo</label>
                    <input type="text" class="form-control" id="machModel">
                </div>
                
                <div class="form-group">
                    <label>Año</label>
                    <input type="number" class="form-control" id="machYear" min="1990" max="2030">
                </div>
                
                <div class="form-group">
                    <label>Precio Diario (€) <span class="req">*</span></label>
                    <input type="number" class="form-control" id="machDailyRate" required step="0.01">
                </div>

                <div class="form-group">
                    <label>Ciudad <span class="req">*</span></label>
                    <input type="text" class="form-control" id="machCity" required>
                </div>

                <div class="form-group">
                    <label>Provincia <span class="req">*</span></label>
                    <input type="text" class="form-control" id="machProvince" required>
                </div>
                
                <div class="form-group">
                    <label>Depósito de Garantía (€)</label>
                    <input type="number" class="form-control" id="machDeposit" step="0.01" value="0">
                </div>
                
                <div class="form-group">
                    <label><input type="checkbox" id="machDelivery"> Entrega disponible</label>
                </div>

                <div class="form-group">
                    <label>Fotos de la máquina <span class="req">*</span></label>
                    <div id="photoUploadArea" class="photo-upload-area" onclick="document.getElementById('machPhotos').click()">
                        <input type="file" id="machPhotos" accept="image/jpeg,image/png,image/webp" multiple style="display:none"
                               onchange="handlePhotoSelect(this, 'photoPreviewGrid', 'photoUploadHint')">
                        <div id="photoUploadHint" class="photo-upload-hint">
                            <span class="photo-upload-icon">📷</span>
                            <span>Haz clic para añadir fotos</span>
                            <small>JPG, PNG o WebP · máx. 5 MB · hasta 10 fotos</small>
                        </div>
                    </div>
                    <div id="photoPreviewGrid" class="photo-preview-grid"></div>
                    <p id="photoError" class="text-danger" style="display:none;font-size:0.85rem;margin-top:0.25rem;"></p>
                </div>

                <div class="form-group">
                    <button type="submit" class="btn btn-success">Publicar Máquina</button>
                    <button type="button" class="btn btn-secondary" onclick="showMyMachinery()">Cancelar</button>
                </div>
            </form>
        </div>
    `;
    // Evitar que el click en la zona de preview propague al área de upload
    document.getElementById('photoPreviewGrid').addEventListener('click', e => e.stopPropagation());
}

/**
 * Maneja el envío del formulario de agregar maquinaria
 */
async function handleAddMachinery(event) {
    event.preventDefault();

    // Validar que haya al menos 1 foto
    if (_pendingFiles.length === 0) {
        const errEl = document.getElementById('photoError');
        if (errEl) { errEl.textContent = t('photos_min_required'); errEl.style.display = 'block'; }
        return;
    }

    const machineryData = {
        title: document.getElementById('machTitle').value,
        description: document.getElementById('machDescription').value,
        machinery_type: document.getElementById('machType').value,
        brand: document.getElementById('machBrand').value || null,
        model: document.getElementById('machModel').value || null,
        year: parseInt(document.getElementById('machYear').value) || null,
        daily_rate: parseFloat(document.getElementById('machDailyRate').value),
        location_city: document.getElementById('machCity').value,
        location_province: document.getElementById('machProvince').value,
        deposit: parseFloat(document.getElementById('machDeposit').value) || 0,
        delivery_available: document.getElementById('machDelivery').checked
    };

    try {
        const created = await apiRequest('/machinery', {
            method: 'POST',
            body: JSON.stringify(machineryData)
        });

        // Subir fotos si hay ficheros pendientes
        if (_pendingFiles.length > 0) {
            await uploadPhotos(created.id, _pendingFiles);
        }

        _pendingFiles = [];
        showAlert('¡Máquina publicada exitosamente!', 'success');
        showMyMachinery();
    } catch (error) {
        showAlert('Error al publicar la máquina: ' + error.message, 'danger');
    }
}

/**
 * Muestra las reservas del usuario
 */
async function showMyBookings() {
    if (!appState.isAuthenticated) {
        showLogin();
        return;
    }
    
    const mainContent = document.getElementById('mainContent');
    mainContent.innerHTML = `
        <div class="container mt-4">
            <h2>Mis Reservas</h2>
            <div id="bookingsGrid"></div>
            <div id="loadingBookings" style="display: none;">
                <div class="spinner"></div>
            </div>
        </div>
    `;
    
    try {
        document.getElementById('loadingBookings').style.display = 'block';
        
        const bookings = await apiRequest('/bookings/my-bookings');
        
        const grid = document.getElementById('bookingsGrid');
        
        if (bookings && bookings.length > 0) {
            bookings.forEach(booking => {
                const bookingCard = createBookingCard(booking);
                grid.appendChild(bookingCard);
            });
        } else {
            grid.innerHTML = '<p class="text-center">No tienes reservas aún.</p>';
        }
    } catch (error) {
        showAlert('Error al cargar reservas', 'danger');
    } finally {
        document.getElementById('loadingBookings').style.display = 'none';
    }
}

/**
 * Crea una tarjeta de reserva
 */
function createBookingCard(booking) {
    const card = document.createElement('div');
    card.className = 'card mb-3';
    
    const statusBadge = getStatusBadge(booking.status);
    
    card.innerHTML = `
        <div class="card-body">
            <h4>Reserva #${booking.id}</h4>
            <p><strong>Máquina ID:</strong> ${booking.machinery_id}</p>
            <p><strong>Fechas:</strong> ${formatDate(booking.start_date)} - ${formatDate(booking.end_date)}</p>
            <p><strong>Total:</strong> ${formatPrice(booking.total_cost)}</p>
            <p><strong>Estado:</strong> ${statusBadge}</p>
            ${booking.status === 'pending' || booking.status === 'confirmed' ? `
                <button class="btn btn-danger" onclick="cancelBooking(${booking.id})">Cancelar Reserva</button>
            ` : ''}
        </div>
    `;
    
    return card;
}

/**
 * Obtiene el badge de estado
 */
function getStatusBadge(status) {
    const badges = {
        'pending': '<span class="badge badge-warning">Pendiente</span>',
        'confirmed': '<span class="badge badge-success">Confirmada</span>',
        'in_progress': '<span class="badge badge-info">En Curso</span>',
        'completed': '<span class="badge badge-success">Completada</span>',
        'cancelled': '<span class="badge badge-danger">Cancelada</span>'
    };
    return badges[status] || status;
}

/**
 * Inicia el proceso de reserva — abre un modal con selector de fechas,
 * resumen de coste en tiempo real y confirmación final.
 */
async function initiateBooking(machineryId) {
    if (!appState.isAuthenticated) {
        showLogin();
        return;
    }

    let machinery;
    try {
        machinery = await apiRequest(`/machinery/${machineryId}`);
    } catch (e) {
        showAlert('Error al cargar los detalles de la máquina', 'danger');
        return;
    }

    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    const tomorrowStr = tomorrow.toISOString().split('T')[0];
    const nextWeek = new Date(today);
    nextWeek.setDate(nextWeek.getDate() + 8);
    const nextWeekStr = nextWeek.toISOString().split('T')[0];

    const deliveryCost = machinery.delivery_cost || 0;

    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.id = 'bookingModal';
    modal.innerHTML = `
        <div class="modal-dialog modal-lg">
            <div class="modal-header">
                <h3>Reservar: ${escHtml(machinery.title)}</h3>
                <button class="modal-close" onclick="document.getElementById('bookingModal').remove()">&times;</button>
            </div>
            <div class="modal-body">
                <div class="detail-info-grid" style="margin-bottom:1rem;">
                    <div><span class="detail-label">Precio diario</span><span><strong>${formatPrice(machinery.daily_rate)}</strong></span></div>
                    ${machinery.weekly_rate ? `<div><span class="detail-label">Precio semanal</span><span>${formatPrice(machinery.weekly_rate)}</span></div>` : ''}
                    <div><span class="detail-label">Depósito garantía</span><span>${formatPrice(machinery.deposit)}</span></div>
                    <div><span class="detail-label">Ubicación</span><span>${escHtml(machinery.location_city)}, ${escHtml(machinery.location_province)}</span></div>
                </div>

                <form id="bookingForm" onsubmit="submitBooking(event, ${machineryId})">
                    <div class="form-row-2">
                        <div class="form-group">
                            <label>Fecha inicio <span class="req">*</span></label>
                            <input type="date" class="form-control" id="bookStart"
                                   min="${tomorrowStr}" value="${tomorrowStr}" required
                                   onchange="updateBookingCost()">
                        </div>
                        <div class="form-group">
                            <label>Fecha fin <span class="req">*</span></label>
                            <input type="date" class="form-control" id="bookEnd"
                                   min="${tomorrowStr}" value="${nextWeekStr}" required
                                   onchange="updateBookingCost()">
                        </div>
                    </div>

                    <div id="bookingCostSummary"
                         data-daily-rate="${machinery.daily_rate}"
                         data-deposit="${machinery.deposit}"
                         data-delivery-cost="${deliveryCost}"
                         style="margin-bottom:1rem;"></div>

                    ${machinery.delivery_available ? `
                    <div class="form-group">
                        <label>
                            <input type="checkbox" id="bookDelivery" onchange="updateBookingCost()">
                            Solicitar entrega${deliveryCost ? ` (+${formatPrice(deliveryCost)})` : ''}
                        </label>
                    </div>
                    <div id="deliveryFields" style="display:none;">
                        <div class="form-row-2">
                            <div class="form-group">
                                <label>Ciudad de entrega</label>
                                <input type="text" class="form-control" id="bookDeliveryCity"
                                       placeholder="Madrid">
                            </div>
                            <div class="form-group">
                                <label>Dirección de entrega</label>
                                <input type="text" class="form-control" id="bookDeliveryAddress"
                                       placeholder="Calle, número...">
                            </div>
                        </div>
                    </div>` : ''}

                    <div class="form-group">
                        <label>Notas o requisitos especiales (opcional)</label>
                        <textarea class="form-control" id="bookNotes" rows="2" maxlength="1000"
                                  placeholder="Ej: necesito operario certificado, acceso por camino secundario..."></textarea>
                    </div>

                    <div style="display:flex;gap:0.5rem;justify-content:flex-end;margin-top:1rem;">
                        <button type="button" class="btn btn-secondary"
                                onclick="document.getElementById('bookingModal').remove()">Cancelar</button>
                        <button type="submit" class="btn btn-primary" id="bookSubmitBtn">Confirmar Reserva</button>
                    </div>
                </form>

                <div id="machineryReviews_${machineryId}" style="margin-top:1.5rem;border-top:1px solid var(--gray-200);padding-top:1rem;"></div>
            </div>
        </div>
    `;

    document.body.appendChild(modal);
    modal.addEventListener('click', e => { if (e.target === modal) modal.remove(); });
    loadReviews('machinery', machineryId, `machineryReviews_${machineryId}`);

    // Show delivery fields when checkbox is toggled
    const deliveryCb = modal.querySelector('#bookDelivery');
    if (deliveryCb) {
        deliveryCb.addEventListener('change', () => {
            const fields = document.getElementById('deliveryFields');
            if (fields) fields.style.display = deliveryCb.checked ? 'block' : 'none';
        });
    }

    updateBookingCost();
}

/**
 * Recalcula y muestra el resumen de coste leyendo fechas del formulario
 */
function updateBookingCost() {
    const summaryEl = document.getElementById('bookingCostSummary');
    const startEl = document.getElementById('bookStart');
    const endEl = document.getElementById('bookEnd');
    if (!summaryEl || !startEl || !endEl) return;

    const dailyRate = parseFloat(summaryEl.dataset.dailyRate);
    const deposit = parseFloat(summaryEl.dataset.deposit);
    const deliveryCost = parseFloat(summaryEl.dataset.deliveryCost || 0);

    const start = startEl.value;
    const end = endEl.value;

    if (!start || !end || end <= start) {
        summaryEl.innerHTML = '<p style="color:var(--danger-color);font-size:0.85rem;">La fecha de fin debe ser posterior a la de inicio.</p>';
        return;
    }

    const days = Math.ceil((new Date(end) - new Date(start)) / 86400000);
    const deliveryCb = document.getElementById('bookDelivery');
    const chargedDelivery = (deliveryCb && deliveryCb.checked) ? deliveryCost : 0;
    const subtotal = days * dailyRate;
    const total = subtotal + chargedDelivery;

    summaryEl.innerHTML = `
        <div class="booking-summary-box">
            <div class="booking-summary-row">
                <span>${days} día${days !== 1 ? 's' : ''} × ${formatPrice(dailyRate)}/día</span>
                <span>${formatPrice(subtotal)}</span>
            </div>
            ${chargedDelivery ? `
            <div class="booking-summary-row">
                <span>Entrega</span><span>${formatPrice(chargedDelivery)}</span>
            </div>` : ''}
            <div class="booking-summary-row booking-summary-total">
                <span>Total alquiler</span><span><strong>${formatPrice(total)}</strong></span>
            </div>
            ${deposit > 0 ? `
            <div class="booking-summary-row" style="color:var(--gray-600);font-size:0.82rem;border-top:none;padding-top:0;">
                <span>+ Depósito de garantía (reembolsable)</span><span>${formatPrice(deposit)}</span>
            </div>` : ''}
        </div>
    `;
}

/**
 * Envía la reserva al backend
 */
async function submitBooking(event, machineryId) {
    event.preventDefault();

    const start = document.getElementById('bookStart').value;
    const end = document.getElementById('bookEnd').value;

    if (!start || !end || end <= start) {
        showAlert('Selecciona fechas válidas (fin posterior a inicio)', 'danger');
        return;
    }

    const deliveryCb = document.getElementById('bookDelivery');
    const needsDelivery = !!(deliveryCb && deliveryCb.checked);

    const payload = {
        machinery_id: machineryId,
        start_date: start + 'T00:00:01',
        end_date: end + 'T23:59:59',
        notes: document.getElementById('bookNotes').value.trim() || null,
        needs_delivery: needsDelivery
    };

    if (needsDelivery) {
        const cityEl = document.getElementById('bookDeliveryCity');
        const addrEl = document.getElementById('bookDeliveryAddress');
        if (cityEl) payload.delivery_city = cityEl.value.trim() || null;
        if (addrEl) payload.delivery_address = addrEl.value.trim() || null;
    }

    const submitBtn = document.getElementById('bookSubmitBtn');
    if (submitBtn) { submitBtn.disabled = true; submitBtn.textContent = 'Reservando...'; }

    try {
        const booking = await apiRequest('/bookings', {
            method: 'POST',
            body: JSON.stringify(payload)
        });
        document.getElementById('bookingModal').remove();
        showAlert(`Reserva #${booking.id} creada. Total: ${formatPrice(booking.total_cost)}. Pendiente de confirmación.`, 'success');
    } catch (e) {
        showAlert('Error al crear la reserva: ' + e.message, 'danger');
        if (submitBtn) { submitBtn.disabled = false; submitBtn.textContent = 'Confirmar Reserva'; }
    }
}

/**
 * Cancela una reserva
 */
async function cancelBooking(bookingId) {
    const reason = prompt('¿Por qué deseas cancelar esta reserva?');
    
    if (!reason) {
        return;
    }
    
    try {
        await apiRequest(`/bookings/${bookingId}/cancel`, {
            method: 'POST',
            body: JSON.stringify({ cancellation_reason: reason })
        });
        
        showAlert('Reserva cancelada correctamente', 'success');
        showMyBookings(); // Recargar
    } catch (error) {
        showAlert('Error al cancelar la reserva', 'danger');
    }
}

/**
 * Muestra todas las máquinas disponibles
 */
function showMachinery() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
    loadInitialMachinery();
}