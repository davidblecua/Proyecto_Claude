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
            renderMachinery(data.machinery);
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
 * Muestra la maquinaria del usuario actual
 */
async function showMyMachinery() {
    if (!appState.isAuthenticated) {
        showLogin();
        return;
    }
    
    const mainContent = document.getElementById('mainContent');
    mainContent.innerHTML = `
        <div class="container mt-4">
            <h2>Mis Máquinas</h2>
            <button class="btn btn-success mb-3" onclick="showAddMachinery()">➕ Agregar Máquina</button>
            <div id="myMachineryGrid" class="card-grid"></div>
            <div id="loadingMyMachinery" style="display: none;">
                <div class="spinner"></div>
            </div>
        </div>
    `;
    
    try {
        document.getElementById('loadingMyMachinery').style.display = 'block';
        
        const data = await apiRequest(`/machinery?owner_id=${appState.currentUser.id}`);
        
        const grid = document.getElementById('myMachineryGrid');
        
        if (data && data.length > 0) {
            data.forEach(machinery => {
                const card = createMyMachineryCard(machinery);
                grid.appendChild(card);
            });
        } else {
            grid.innerHTML = '<p class="text-center">No has publicado ninguna máquina aún.</p>';
        }
    } catch (error) {
        showAlert('Error al cargar tus máquinas', 'danger');
    } finally {
        document.getElementById('loadingMyMachinery').style.display = 'none';
    }
}

/**
 * Crea una tarjeta de maquinaria propia con opciones de edición
 */
function createMyMachineryCard(machinery) {
    const card = document.createElement('div');
    card.className = 'card';
    
    card.innerHTML = `
        <div class="card-body">
            <h3 class="card-title">${machinery.title}</h3>
            <p class="card-text">
                <span class="badge badge-info">${translateMachineryType(machinery.machinery_type)}</span>
                ${machinery.is_available 
                    ? '<span class="badge badge-success">Disponible</span>' 
                    : '<span class="badge badge-warning">No disponible</span>'}
            </p>
            <p class="card-text">${machinery.location_city}, ${machinery.location_province}</p>
            <p class="card-text"><strong>${formatPrice(machinery.daily_rate)}/día</strong></p>
            <div class="mt-2">
                <button class="btn btn-primary" onclick="toggleAvailability(${machinery.id}, ${!machinery.is_available})">
                    ${machinery.is_available ? '❌ Marcar no disponible' : '✅ Marcar disponible'}
                </button>
                <button class="btn btn-danger" onclick="deleteMachinery(${machinery.id})">🗑️ Eliminar</button>
            </div>
        </div>
    `;
    
    return card;
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
                    <label>Título</label>
                    <input type="text" class="form-control" id="machTitle" required>
                </div>
                
                <div class="form-group">
                    <label>Descripción</label>
                    <textarea class="form-control" id="machDescription" rows="4" required></textarea>
                </div>
                
                <div class="form-group">
                    <label>Tipo de Maquinaria</label>
                    <select class="form-control" id="machType" required>
                        <option value="excavadora">Excavadora</option>
                        <option value="dumper">Dumper</option>
                        <option value="grua_torre">Grúa Torre</option>
                        <option value="plataforma_elevadora">Plataforma Elevadora</option>
                        <option value="compactadora">Compactadora</option>
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
                    <label>Precio Diario (€)</label>
                    <input type="number" class="form-control" id="machDailyRate" required step="0.01">
                </div>
                
                <div class="form-group">
                    <label>Ciudad</label>
                    <input type="text" class="form-control" id="machCity" required>
                </div>
                
                <div class="form-group">
                    <label>Provincia</label>
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
                    <button type="submit" class="btn btn-success">Publicar Máquina</button>
                    <button type="button" class="btn btn-secondary" onclick="showMyMachinery()">Cancelar</button>
                </div>
            </form>
        </div>
    `;
}

/**
 * Maneja el envío del formulario de agregar maquinaria
 */
async function handleAddMachinery(event) {
    event.preventDefault();
    
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
        await apiRequest('/machinery', {
            method: 'POST',
            body: JSON.stringify(machineryData)
        });
        
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
 * Inicia el proceso de reserva
 */
function initiateBooking(machineryId) {
    // Aquí se implementaría un formulario de reserva más completo
    showAlert('Funcionalidad de reserva en desarrollo', 'info');
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