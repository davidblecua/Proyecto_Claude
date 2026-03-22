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
                    <label for="loginEmail">Email</label>
                    <input type="email" class="form-control" id="loginEmail" required>
                </div>
                <div class="form-group">
                    <label for="loginPassword">Contraseña</label>
                    <input type="password" class="form-control" id="loginPassword" required>
                </div>
                <div class="form-group">
                    <button type="submit" class="btn btn-primary" style="width: 100%;">Iniciar Sesión</button>
                </div>
                <div class="text-center mt-2">
                    <p>¿No tienes cuenta? <a href="#" onclick="showRegister()">Regístrate aquí</a></p>
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
                    <label for="regEmail">Email</label>
                    <input type="email" class="form-control" id="regEmail" required>
                </div>
                <div class="form-group">
                    <label for="regUsername">Nombre de Usuario</label>
                    <input type="text" class="form-control" id="regUsername" required>
                </div>
                <div class="form-group">
                    <label for="regFullName">Nombre Completo</label>
                    <input type="text" class="form-control" id="regFullName" required>
                </div>
                <div class="form-group">
                    <label for="regPassword">Contraseña</label>
                    <input type="password" class="form-control" id="regPassword" required 
                           minlength="8" placeholder="Mín. 8 caracteres, 1 número, 1 mayúscula">
                    <small>Debe contener al menos 8 caracteres, un número y una mayúscula</small>
                </div>
                <div class="form-group">
                    <label for="regRole">Tipo de Usuario</label>
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
 * Muestra el dashboard del usuario
 */
async function showDashboard() {
    if (!appState.isAuthenticated) {
        showLogin();
        return;
    }
    
    const user = appState.currentUser;
    const mainContent = document.getElementById('mainContent');
    
    mainContent.innerHTML = `
        <div class="container mt-4">
            <h1>Bienvenido, ${user.full_name}</h1>
            <p><strong>Rol:</strong> ${translateRole(user.role)}</p>
            <p><strong>Email:</strong> ${user.email}</p>
            
            <div class="card-grid mt-4">
                <div class="card">
                    <div class="card-body">
                        <h3>👤 Mi Perfil</h3>
                        <p>Ver y editar información personal</p>
                        <button class="btn btn-primary" onclick="showProfile()">Ver Perfil</button>
                    </div>
                </div>
                
                ${user.role !== 'consumer' ? `
                <div class="card">
                    <div class="card-body">
                        <h3>🏗️ Mis Máquinas</h3>
                        <p>Gestionar maquinaria publicada</p>
                        <button class="btn btn-primary" onclick="showMyMachinery()">Ver Máquinas</button>
                    </div>
                </div>
                <div class="card">
                    <div class="card-body">
                        <h3>➕ Publicar Máquina</h3>
                        <p>Agregar nueva maquinaria</p>
                        <button class="btn btn-success" onclick="showAddMachinery()">Publicar</button>
                    </div>
                </div>
                ` : ''}
                
                <div class="card">
                    <div class="card-body">
                        <h3>📅 Mis Reservas</h3>
                        <p>Ver historial de reservas</p>
                        <button class="btn btn-primary" onclick="showMyBookings()">Ver Reservas</button>
                    </div>
                </div>
            </div>
        </div>
    `;
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
                <h2>${user.full_name || user.username}</h2>
                <span class="role-badge">${translateRole(user.role)}</span>
            </div>

            <div class="profile-info-row">
                <span class="profile-info-label">Nombre</span>
                <span class="profile-info-value">${user.full_name || '—'}</span>
            </div>
            <div class="profile-info-row">
                <span class="profile-info-label">Usuario</span>
                <span class="profile-info-value">@${user.username}</span>
            </div>
            <div class="profile-info-row">
                <span class="profile-info-label">Email</span>
                <span class="profile-info-value">${user.email}</span>
            </div>
            <div class="profile-info-row">
                <span class="profile-info-label">Teléfono</span>
                <span class="profile-info-value">${user.phone || '—'}</span>
            </div>
            <div class="profile-info-row">
                <span class="profile-info-label">Empresa</span>
                <span class="profile-info-value">${user.company_name || '—'}</span>
            </div>
            <div class="profile-info-row">
                <span class="profile-info-label">Rol</span>
                <span class="profile-info-value">${translateRole(user.role)}</span>
            </div>

            <div style="margin-top:2rem;">
                <button class="btn btn-primary" onclick="showDashboard()">Volver al Panel</button>
            </div>
        </div>
    `;
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