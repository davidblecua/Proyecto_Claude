/**
 * RentaMaq - Gestión de Autenticación
 * Maneja login, registro y gestión de tokens
 */

/**
 * Muestra el formulario de login
 */
function showLogin() {
    const mainContent = document.getElementById('mainContent');
    mainContent.innerHTML = `
        <div class="form-container">
            <h2>Iniciar Sesión</h2>
            <form id="loginForm" onsubmit="handleLogin(event)">
                <div class="form-group">
                    <label for="loginEmail">Email <span class="req">*</span></label>
                    <input type="email" class="form-control" id="loginEmail" required>
                </div>
                <div class="form-group">
                    <label for="loginPassword">Contraseña <span class="req">*</span></label>
                    <input type="password" class="form-control" id="loginPassword" required>
                </div>
                <div class="form-group">
                    <button type="submit" class="btn btn-primary" style="width: 100%;">Iniciar Sesión</button>
                </div>
                <div class="text-center mt-2">
                    <p>¿No tienes cuenta? <a href="#" onclick="showRegister()">Regístrate aquí</a></p>
                    <p><a href="#" onclick="showForgotPassword()" style="font-size:0.88rem;color:var(--gray-600);">¿Olvidaste tu contraseña?</a></p>
                </div>
                <hr>
                <div class="form-group">
                    <a href="/api/v1/auth/google" class="btn" style="width:100%;background:#fff;border:1px solid #ddd;display:flex;align-items:center;justify-content:center;gap:10px;">
                        <img src="https://www.google.com/favicon.ico" width="18"> Iniciar sesión con Google
                    </a>
                </div>
            </form>
        </div>
    `;
}

/**
 * Maneja el login
 */
async function handleLogin(event) {
    event.preventDefault();
    
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    
    try {
        const data = await apiRequest('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });
        
        // Guardar tokens y usuario
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('refresh_token', data.refresh_token);
        localStorage.setItem('current_user', JSON.stringify(data.user));
        
        appState.authToken = data.access_token;
        appState.currentUser = data.user;
        appState.isAuthenticated = true;

        // Sincronizar idioma desde el perfil del usuario
        if (data.user.preferred_language && typeof setLang === 'function') {
            setLang(data.user.preferred_language);
        }

        updateNavbarForAuthenticatedUser();
        showAlert('¡Bienvenido, ' + data.user.full_name + '!', 'success');
        
        // Redirigir al dashboard
        showDashboard();
    } catch (error) {
        showAlert('Error al iniciar sesión: ' + error.message, 'danger');
    }
}

/**
 * Muestra el formulario de registro
 */
function showRegister() {
    const mainContent = document.getElementById('mainContent');
    mainContent.innerHTML = `
        <div class="form-container">
            <h2>Registrarse</h2>
            <form id="registerForm" onsubmit="handleRegister(event)">
                <div class="form-group">
                    <label for="regEmail">Email <span class="req">*</span></label>
                    <input type="email" class="form-control" id="regEmail" required>
                </div>
                <div class="form-group">
                    <label for="regUsername">Nombre de Usuario <span class="req">*</span></label>
                    <input type="text" class="form-control" id="regUsername" required>
                </div>
                <div class="form-group">
                    <label for="regFullName">Nombre Completo <span class="req">*</span></label>
                    <input type="text" class="form-control" id="regFullName" required>
                </div>
                <div class="form-group">
                    <label for="regPassword">Contraseña <span class="req">*</span></label>
                    <input type="password" class="form-control" id="regPassword" required
                           minlength="8" placeholder="Mín. 8 caracteres, 1 número, 1 mayúscula">
                    <small>Debe contener al menos 8 caracteres, un número y una mayúscula</small>
                </div>
                <div class="form-group">
                    <label for="regRole">Tipo de Usuario <span class="req">*</span></label>
                    <select class="form-control" id="regRole" required>
                        <option value="consumer">Consumidor (Alquilar máquinas)</option>
                        <option value="publisher">Publicador (Alquilar y publicar)</option>
                        <option value="admin">Administrador de Empresa</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="regPhone">Teléfono</label>
                    <input type="tel" class="form-control" id="regPhone" placeholder="+34 600 000 000">
                </div>
                <div class="form-group">
                    <label for="regCompany">Empresa (opcional)</label>
                    <input type="text" class="form-control" id="regCompany">
                </div>
                <div class="form-group">
                    <button type="submit" class="btn btn-primary" style="width: 100%;">Registrarse</button>
                </div>
                <div class="text-center mt-2">
                    <p>¿Ya tienes cuenta? <a href="#" onclick="showLogin()">Inicia sesión aquí</a></p>
                </div>
                <hr>
                <div class="form-group">
                    <a href="/api/v1/auth/google" class="btn" style="width:100%;background:#fff;border:1px solid #ddd;display:flex;align-items:center;justify-content:center;gap:10px;">
                        <img src="https://www.google.com/favicon.ico" width="18"> Registrarse con Google
                    </a>
                </div>
            </form>
        </div>
    `;
}

/**
 * Maneja el registro
 */
async function handleRegister(event) {
    event.preventDefault();
    
    const userData = {
        email: document.getElementById('regEmail').value,
        username: document.getElementById('regUsername').value,
        full_name: document.getElementById('regFullName').value,
        password: document.getElementById('regPassword').value,
        role: document.getElementById('regRole').value,
        phone: document.getElementById('regPhone').value || null,
        company_name: document.getElementById('regCompany').value || null
    };
    
    try {
        await apiRequest('/auth/register', {
            method: 'POST',
            body: JSON.stringify(userData)
        });
        
        showAlert('¡Registro exitoso! Por favor, inicia sesión.', 'success');
        showLogin();
    } catch (error) {
        showAlert('Error en el registro: ' + error.message, 'danger');
    }
}

/**
 * Muestra el dashboard del usuario con KPIs
 */
async function showDashboard() {
    if (!appState.isAuthenticated) {
        showLogin();
        return;
    }

    const user = appState.currentUser;
    const mainContent = document.getElementById('mainContent');
    const isPublisher = user.role !== 'consumer';

    mainContent.innerHTML = `
        <div class="container mt-4">
            <div class="dashboard-welcome">
                <div class="avatar-wrapper-sm" onclick="showProfile()" title="Ver perfil" style="cursor:pointer;">
                    <img src="${getUserAvatar()}" alt="Perfil" class="avatar-nav" style="width:48px;height:48px;">
                </div>
                <div>
                    <h1 style="margin:0;">Bienvenido, ${escHtml(user.full_name.split(' ')[0])}</h1>
                    <span class="role-badge">${translateRole(user.role)}</span>
                </div>
            </div>

            <!-- KPI Cards -->
            <div class="kpi-grid" id="kpiGrid">
                <div class="kpi-card kpi-loading">Cargando estadísticas...</div>
            </div>

            <!-- Acciones rápidas -->
            <div class="dashboard-section">
                <h3>Acciones Rápidas</h3>
                <div class="quick-actions">
                    <button class="btn btn-primary" onclick="showProfile()">Mi Perfil</button>
                    <button class="btn btn-primary" onclick="showMyBookings()">Mis Reservas</button>
                    ${isPublisher ? `
                    <button class="btn btn-success" onclick="showMyMachinery()">Gestionar Máquinas</button>
                    <button class="btn btn-success" onclick="showAddMachinery()">Publicar Máquina</button>
                    <button class="btn btn-success" onclick="showMyOperators()">Mis Operarios</button>
                    <button class="btn btn-success" onclick="showPublishOperator()">Publicar Operario</button>
                    ` : ''}
                    <button class="btn btn-secondary" onclick="window.location.href='/'">Buscar Maquinaria</button>
                </div>
            </div>

            <!-- Últimas reservas -->
            <div class="dashboard-section">
                <h3>${isPublisher ? 'Últimas Reservas Recibidas' : 'Mis Últimas Reservas'}</h3>
                <div id="recentBookingsList">
                    <div class="spinner-sm"></div>
                </div>
            </div>

            <!-- Reservas de operarios -->
            <div class="dashboard-section">
                <h3>Mis Reservas de Operarios</h3>
                <div id="opBookingsContainer">
                    <div class="spinner-sm"></div>
                </div>
            </div>
        </div>
    `;

    // Cargar stats desde la API
    try {
        const stats = await apiRequest('/dashboard/stats');
        renderDashboardKPIs(stats, isPublisher);
        renderRecentBookings(stats.recent_bookings, isPublisher);
    } catch (e) {
        document.getElementById('kpiGrid').innerHTML = '<p class="text-center">No se pudieron cargar las estadísticas.</p>';
        document.getElementById('recentBookingsList').innerHTML = '';
    }

    // Cargar reservas de operarios (definida en operators.js)
    if (typeof showMyOperatorBookings === 'function') showMyOperatorBookings();
}

function renderDashboardKPIs(stats, isPublisher) {
    const grid = document.getElementById('kpiGrid');
    if (isPublisher) {
        grid.innerHTML = `
            <div class="kpi-card">
                <div class="kpi-icon kpi-icon-text">M</div>
                <div class="kpi-value">${stats.total_machinery}</div>
                <div class="kpi-label">Máquinas Publicadas</div>
            </div>
            <div class="kpi-card kpi-green">
                <div class="kpi-icon kpi-icon-text">R</div>
                <div class="kpi-value">${stats.active_bookings}</div>
                <div class="kpi-label">Reservas Activas</div>
            </div>
            <div class="kpi-card kpi-orange">
                <div class="kpi-icon kpi-icon-text">P</div>
                <div class="kpi-value">${stats.pending_bookings}</div>
                <div class="kpi-label">Reservas Pendientes</div>
            </div>
            <div class="kpi-card kpi-blue">
                <div class="kpi-icon kpi-icon-text">€</div>
                <div class="kpi-value">${formatPrice(stats.monthly_revenue)}</div>
                <div class="kpi-label">Ingresos este mes</div>
            </div>
        `;
    } else {
        grid.innerHTML = `
            <div class="kpi-card kpi-green">
                <div class="kpi-icon kpi-icon-text">R</div>
                <div class="kpi-value">${stats.active_bookings}</div>
                <div class="kpi-label">Reservas Activas</div>
            </div>
            <div class="kpi-card kpi-orange">
                <div class="kpi-icon kpi-icon-text">P</div>
                <div class="kpi-value">${stats.pending_bookings}</div>
                <div class="kpi-label">Reservas Pendientes</div>
            </div>
            <div class="kpi-card kpi-blue">
                <div class="kpi-icon kpi-icon-text">C</div>
                <div class="kpi-value">${stats.completed_bookings}</div>
                <div class="kpi-label">Completadas</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-icon kpi-icon-text">€</div>
                <div class="kpi-value">${formatPrice(stats.total_spent)}</div>
                <div class="kpi-label">Total gastado</div>
            </div>
        `;
    }
}

function renderRecentBookings(bookings, isPublisher) {
    const container = document.getElementById('recentBookingsList');
    if (!bookings || bookings.length === 0) {
        container.innerHTML = '<p class="text-center" style="color:var(--gray-600);">No hay reservas recientes.</p>';
        return;
    }
    container.innerHTML = bookings.map(b => `
        <div class="recent-booking-row">
            <div class="recent-booking-info">
                <strong>${b.machinery_title}</strong>
                ${isPublisher ? `<span style="color:var(--gray-600);font-size:0.85rem;"> · ${b.requester_name || ''}</span>` : ''}
                <div style="font-size:0.82rem;color:var(--gray-500);">${b.start_date ? b.start_date.split('T')[0] : ''} — ${b.end_date ? b.end_date.split('T')[0] : ''}</div>
            </div>
            <div style="display:flex;align-items:center;gap:0.5rem;">
                ${getStatusBadge(b.status)}
                <strong>${formatPrice(b.total_cost)}</strong>
            </div>
        </div>
    `).join('');
}

/**
 * Traduce el rol al español
 */
function translateRole(role) {
    const roles = {
        'consumer': 'Consumidor',
        'publisher': 'Publicador',
        'admin': 'Administrador'
    };
    return roles[role] || role;
}

/**
 * Muestra el perfil del usuario con foto y datos personales
 */
function showProfile() {
    if (!appState.isAuthenticated) { showLogin(); return; }

    const user = appState.currentUser;
    const currentPhoto = getUserAvatar();
    const mainContent = document.getElementById('mainContent');

    mainContent.innerHTML = `
        <div class="profile-card">
            <div class="profile-header">
                <div class="avatar-wrapper" onclick="document.getElementById('photoInput').click()" title="Haz clic para cambiar la foto">
                    <img id="profileAvatar" src="${currentPhoto}" alt="Foto de perfil" class="avatar-lg">
                    <div class="avatar-edit-overlay">Cambiar foto</div>
                </div>
                <input type="file" id="photoInput" accept="image/*" style="display:none" onchange="changeProfilePhoto(event)">
                <p style="color:var(--gray-500);font-size:0.82rem;margin-top:0.4rem;">Haz clic en la foto para cambiarla</p>
                <h2>${escHtml(user.full_name || user.username)}</h2>
                <span class="role-badge">${translateRole(user.role)}</span>
            </div>

            <div class="profile-info-row">
                <span class="profile-info-label">Nombre</span>
                <span class="profile-info-value">${escHtml(user.full_name || '—')}</span>
            </div>
            <div class="profile-info-row">
                <span class="profile-info-label">Usuario</span>
                <span class="profile-info-value">@${escHtml(user.username)}</span>
            </div>
            <div class="profile-info-row">
                <span class="profile-info-label">Email</span>
                <span class="profile-info-value">${escHtml(user.email)}</span>
            </div>
            <div class="profile-info-row">
                <span class="profile-info-label">Teléfono</span>
                <span class="profile-info-value">${escHtml(user.phone || '—')}</span>
            </div>
            <div class="profile-info-row">
                <span class="profile-info-label">Empresa</span>
                <span class="profile-info-value">${escHtml(user.company_name || '—')}</span>
            </div>
            <div class="profile-info-row">
                <span class="profile-info-label">Rol</span>
                <span class="profile-info-value">${translateRole(user.role)}</span>
            </div>
            <div class="profile-info-row" style="align-items:center;">
                <span class="profile-info-label">Idioma</span>
                <span class="profile-info-value">
                    <select id="profileLangSelect" class="form-control" style="max-width:140px;display:inline-block;"
                            onchange="saveProfileLanguage(this.value)">
                        <option value="es" ${(user.preferred_language||'es')==='es'?'selected':''}>Español</option>
                        <option value="ca" ${(user.preferred_language||'es')==='ca'?'selected':''}>Català</option>
                        <option value="en" ${(user.preferred_language||'es')==='en'?'selected':''}>English</option>
                    </select>
                </span>
            </div>

            <div style="margin-top:2rem;">
                <button class="btn btn-primary" onclick="showDashboard()">Volver al Panel</button>
            </div>
        </div>
    `;
}

/**
 * Guarda el idioma preferido del usuario en el backend y actualiza la UI.
 */
async function saveProfileLanguage(lang) {
    try {
        const updated = await apiRequest('/users/me/language', {
            method: 'PATCH',
            body: JSON.stringify({ language: lang }),
        });
        // Actualizar estado local
        appState.currentUser.preferred_language = lang;
        localStorage.setItem('current_user', JSON.stringify(appState.currentUser));
        if (typeof setLang === 'function') setLang(lang);
        showAlert('Idioma actualizado', 'success');
    } catch (e) {
        showAlert('No se pudo guardar el idioma: ' + e.message, 'danger');
    }
}

/**
 * Cambia la foto de perfil: lee el archivo seleccionado, lo convierte a base64
 * y lo guarda en localStorage (clave por user.id para no mezclar usuarios)
 */
function changeProfilePhoto(event) {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = function(e) {
        const base64 = e.target.result;
        const key = 'profile_photo_' + appState.currentUser.id;
        localStorage.setItem(key, base64);

        // Actualizar la foto grande en la página de perfil
        const profileAvatar = document.getElementById('profileAvatar');
        if (profileAvatar) profileAvatar.src = base64;

        // Actualizar también el avatar pequeño en la navbar
        const navAvatar = document.getElementById('navAvatar');
        if (navAvatar) navAvatar.src = base64;

        showAlert('Foto de perfil actualizada', 'success');
    };
    reader.readAsDataURL(file);
}

/**
 * Muestra el formulario de recuperación de contraseña (paso 1: introducir email)
 */
function showForgotPassword() {
    const mainContent = document.getElementById('mainContent');
    mainContent.innerHTML = `
        <div class="form-container">
            <h2>Recuperar Contraseña</h2>
            <p style="color:var(--gray-600);margin-bottom:1.5rem;">
                Introduce tu email y recibirás un enlace para crear una nueva contraseña.
            </p>
            <form id="forgotForm" onsubmit="handleForgotPassword(event)">
                <div class="form-group">
                    <label for="forgotEmail">Email <span class="req">*</span></label>
                    <input type="email" class="form-control" id="forgotEmail" required autofocus>
                </div>
                <div class="form-group">
                    <button type="submit" class="btn btn-primary" style="width:100%;" id="forgotBtn">
                        Enviar instrucciones
                    </button>
                </div>
                <div class="text-center mt-2">
                    <p><a href="#" onclick="showLogin()">← Volver al inicio de sesión</a></p>
                </div>
            </form>
        </div>
    `;
}

/**
 * Envía la solicitud de recuperación de contraseña
 */
async function handleForgotPassword(event) {
    event.preventDefault();
    const email = document.getElementById('forgotEmail').value;
    const btn = document.getElementById('forgotBtn');
    btn.disabled = true;
    btn.textContent = 'Enviando...';

    try {
        const data = await apiRequest('/auth/forgot-password', {
            method: 'POST',
            body: JSON.stringify({ email })
        });
        const mainContent = document.getElementById('mainContent');
        mainContent.innerHTML = `
            <div class="form-container" style="text-align:center;">
                <h2>Revisa tu correo</h2>
                <p style="color:var(--gray-600);">${escHtml(data.message)}</p>
                <button class="btn btn-secondary mt-3" onclick="showLogin()">← Volver al login</button>
            </div>
        `;
    } catch (e) {
        showAlert('Error: ' + e.message, 'danger');
        btn.disabled = false;
        btn.textContent = 'Enviar instrucciones';
    }
}

/**
 * Muestra el formulario de nueva contraseña (paso 2: introducir nueva contraseña)
 * @param {string} token - Token de recuperación recibido por email / URL
 */
function showResetPassword(token) {
    const mainContent = document.getElementById('mainContent');
    mainContent.innerHTML = `
        <div class="form-container">
            <h2>Nueva Contraseña</h2>
            <p style="color:var(--gray-600);margin-bottom:1.5rem;">
                Introduce tu nueva contraseña. Debe tener al menos 8 caracteres, un número y una mayúscula.
            </p>
            <form id="resetForm" onsubmit="handleResetPassword(event, ${JSON.stringify(token)})">
                <div class="form-group">
                    <label for="resetPwd">Nueva contraseña <span class="req">*</span></label>
                    <input type="password" class="form-control" id="resetPwd" required
                           minlength="8" placeholder="Mín. 8 caracteres, 1 número, 1 mayúscula" autofocus>
                </div>
                <div class="form-group">
                    <label for="resetPwd2">Confirmar contraseña <span class="req">*</span></label>
                    <input type="password" class="form-control" id="resetPwd2" required minlength="8">
                </div>
                <div class="form-group">
                    <button type="submit" class="btn btn-primary" style="width:100%;" id="resetBtn">
                        Guardar nueva contraseña
                    </button>
                </div>
            </form>
        </div>
    `;
}

/**
 * Envía la nueva contraseña al backend
 */
async function handleResetPassword(event, token) {
    event.preventDefault();
    const pwd = document.getElementById('resetPwd').value;
    const pwd2 = document.getElementById('resetPwd2').value;

    if (pwd !== pwd2) {
        showAlert('Las contraseñas no coinciden', 'danger');
        return;
    }

    const btn = document.getElementById('resetBtn');
    btn.disabled = true;
    btn.textContent = 'Guardando...';

    try {
        const data = await apiRequest('/auth/reset-password', {
            method: 'POST',
            body: JSON.stringify({ token, new_password: pwd })
        });
        const mainContent = document.getElementById('mainContent');
        mainContent.innerHTML = `
            <div class="form-container" style="text-align:center;">
                <h2>Contraseña actualizada</h2>
                <p style="color:var(--gray-600);">${escHtml(data.message)}</p>
                <button class="btn btn-primary mt-3" onclick="showLogin()">Iniciar sesión</button>
            </div>
        `;
    } catch (e) {
        showAlert('Error: ' + e.message, 'danger');
        btn.disabled = false;
        btn.textContent = 'Guardar nueva contraseña';
    }
}