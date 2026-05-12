"""
Servicio de almacenamiento local para imágenes de maquinaria.
Guarda ficheros en frontend/static/uploads/machines/{machine_id}/
y los sirve como /static/uploads/machines/{machine_id}/{filename}.
"""
import os
import uuid
from pathlib import Path
from typing import Tuple

from fastapi import UploadFile, HTTPException, status

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
MAX_PHOTOS = 10

# Raíz del proyecto: backend/ está dentro de 01_codigo/
_BACKEND_DIR = Path(__file__).resolve().parent.parent.parent   # → 01_codigo/backend
_STATIC_DIR = _BACKEND_DIR.parent / "frontend" / "static"
UPLOAD_BASE: Path = _STATIC_DIR / "uploads" / "machines"


def _detect_image_ext(header: bytes) -> str | None:
    """Devuelve extensión ('jpg','png','webp') o None si el tipo no está permitido."""
    if header[:3] == b'\xff\xd8\xff':
        return 'jpg'
    if header[:8] == b'\x89PNG\r\n\x1a\n':
        return 'png'
    if header[:4] == b'RIFF' and header[8:12] == b'WEBP':
        return 'webp'
    return None


async def validate_and_read(file: UploadFile) -> Tuple[bytes, str]:
    """
    Lee el fichero, valida MIME por magic bytes y tamaño.
    Devuelve (contenido, extensión).
    Lanza HTTPException 422 si no es válido.
    """
    content = await file.read()

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"La imagen '{file.filename}' supera el tamaño máximo de 5 MB."
        )

    header = content[:12]
    ext = _detect_image_ext(header)
    if ext is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Formato no permitido: '{file.filename}'. Usa JPG, PNG o WebP."
        )

    return content, ext


def save_file(content: bytes, ext: str, machine_id: int) -> str:
    """
    Guarda el fichero en disco y devuelve la URL pública (/static/...).
    """
    folder = UPLOAD_BASE / str(machine_id)
    folder.mkdir(parents=True, exist_ok=True)

    filename = f"{uuid.uuid4().hex}.{ext}"
    (folder / filename).write_bytes(content)

    return f"/static/uploads/machines/{machine_id}/{filename}"


def delete_file(url: str) -> None:
    """
    Elimina el fichero del disco dado su URL pública.
    Si no existe, no lanza error.
    """
    if not url.startswith("/static/uploads/machines/"):
        return  # no borrar imágenes externas (seeds, etc.)
    relative = url.removeprefix("/static/")
    path = _STATIC_DIR / relative
    try:
        path.unlink()
    except FileNotFoundError:
        pass
