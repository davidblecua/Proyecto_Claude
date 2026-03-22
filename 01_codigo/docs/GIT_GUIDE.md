# Guía Rápida - Configuración Git y Primeros Pasos

## Configurar Git

### 1. Configuración Inicial

```bash
# Configurar nombre y email (requerido)
git config --global user.name "Tu Nombre"
git config --global user.email "tu-email@ejemplo.com"

# Verificar configuración
git config --list
```

### 2. Conectar con GitHub/GitLab

```bash
# Crear un repositorio nuevo en GitHub/GitLab primero
# Luego conectarlo:

git remote add origin https://github.com/tu-usuario/rentamaq-platform.git

# O con SSH (recomendado):
git remote add origin git@github.com:tu-usuario/rentamaq-platform.git
```

### 3. Primer Commit

```bash
# Ver estado de archivos
git status

# Agregar todos los archivos
git add .

# Hacer el primer commit
git commit -m "Initial commit: RentaMaq v0.1"

# Subir a GitHub/GitLab
git branch -M main  # Renombrar rama a 'main'
git push -u origin main
```

## Flujo de Trabajo Git

### Comandos Básicos Diarios

```bash
# Ver estado
git status

# Agregar archivos modificados
git add .
# O archivos específicos:
git add backend/app/main.py

# Hacer commit
git commit -m "Descripción del cambio"

# Subir cambios
git push

# Descargar cambios
git pull
```

### Crear Ramas para Nuevas Características

```bash
# Crear y cambiar a nueva rama
git checkout -b feature/nueva-funcionalidad

# Hacer cambios y commits
git add .
git commit -m "Agregar nueva funcionalidad"

# Subir rama
git push -u origin feature/nueva-funcionalidad

# Volver a la rama principal
git checkout main

# Fusionar rama (después de aprobar Pull Request)
git merge feature/nueva-funcionalidad
```

## Comandos Útiles

```bash
# Ver historial de commits
git log
git log --oneline  # Versión compacta

# Ver diferencias
git diff

# Deshacer cambios no commiteados
git checkout -- archivo.py

# Deshacer último commit (mantener cambios)
git reset --soft HEAD~1

# Ver ramas
git branch -a

# Eliminar rama local
git branch -d nombre-rama

# Guardar cambios temporalmente
git stash
git stash pop  # Recuperar cambios
```

## Ignorar Archivos

El archivo `.gitignore` ya está configurado para ignorar:
- Archivos de Python (`__pycache__`, `*.pyc`)
- Entornos virtuales (`venv/`)
- Variables de entorno (`.env`)
- Archivos de IDE

## Mejores Prácticas

1. **Commits frecuentes**: Haz commits pequeños y frecuentes
2. **Mensajes descriptivos**: Usa mensajes claros ("Agregar endpoint de búsqueda")
3. **Nunca subir .env**: Las credenciales deben quedar en local
4. **Usar ramas**: Crea ramas para nuevas características
5. **Pull antes de Push**: Siempre haz `git pull` antes de subir cambios

## Mensajes de Commit Recomendados

```bash
# Formato: <tipo>: <descripción>

git commit -m "feat: Agregar endpoint de búsqueda de maquinaria"
git commit -m "fix: Corregir error en validación de fechas"
git commit -m "docs: Actualizar documentación de API"
git commit -m "style: Mejorar estilos del navbar"
git commit -m "refactor: Reorganizar servicios de usuario"
git commit -m "test: Agregar tests para autenticación"
```

## Solución de Problemas Git

### Error: "Permission denied (publickey)"

```bash
# Generar nueva clave SSH
ssh-keygen -t ed25519 -C "tu-email@ejemplo.com"

# Copiar clave pública
cat ~/.ssh/id_ed25519.pub

# Agregar en GitHub: Settings > SSH and GPG keys > New SSH key
```

### Error: "Merge conflict"

```bash
# Ver archivos con conflicto
git status

# Editar archivos manualmente, buscar:
# <<<<<<< HEAD
# Tu código
# =======
# Código del otro
# >>>>>>> rama

# Después de resolver:
git add archivo-resuelto.py
git commit -m "Resolver conflicto de merge"
```

### Deshacer cambios subidos

```bash
# Deshacer último commit remoto (usar con precaución)
git revert HEAD
git push
```

## Próximos Pasos

1. Crea un repositorio en GitHub/GitLab
2. Configura Git localmente
3. Sube el proyecto
4. Invita colaboradores si es necesario
5. Configura CI/CD (opcional)

Para más ayuda: https://git-scm.com/doc
