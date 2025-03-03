import logging
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from typing import Dict, Any, Optional
from pydantic import BaseModel

from ..services.auth_service import verify_authorization
from ..services.data_retrieval_service import (
    create_retrieval_task,
    start_retrieval_task,
    upload_image_to_task
)

# Configurar logging
logger = logging.getLogger(__name__)

# Crear router
router = APIRouter(prefix="/api/bff/v1")

# Modelos Pydantic
class CreateTaskRequest(BaseModel):
    source_type: str
    source_name: str
    source_id: str
    location: str
    retrieval_method: str
    batch_id: str
    priority: int = 0
    metadata: Optional[Dict[str, Any]] = None

# Endpoints

@router.post("/data-retrieval/tasks", status_code=201)
async def api_create_task(
    request: CreateTaskRequest
):
    """
    Endpoint para crear una tarea de recuperación de imágenes.
    Primero verifica autorización con el servicio auth y luego reenvía al servicio data-retrieval.
    """
    # Verificar autorización
    is_authorized = await verify_authorization()
    if not is_authorized:
        logger.warning("Intento de acceso no autorizado al crear tarea")
        raise HTTPException(status_code=401, detail="No autorizado para acceder a este recurso")
    
    logger.info(f"Creando tarea de recuperación para {request.source_name}")
    
    # Si está autorizado, llamar al servicio de recuperación de datos
    try:
        response = await create_retrieval_task(request)
        logger.info(f"Tarea creada con éxito. ID: {response.get('task_id', 'N/A')}")
        return response
    except Exception as e:
        logger.error(f"Error al crear tarea: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error de comunicación con el servicio: {str(e)}")

@router.post("/data-retrieval/tasks/{task_id}/start")
async def api_start_task(
    task_id: str
):
    """
    Endpoint para iniciar una tarea de recuperación.
    Primero verifica autorización con el servicio auth y luego reenvía al servicio data-retrieval.
    """
    # Verificar autorización
    is_authorized = await verify_authorization()
    if not is_authorized:
        logger.warning(f"Intento de acceso no autorizado al iniciar tarea {task_id}")
        raise HTTPException(status_code=401, detail="No autorizado para acceder a este recurso")
    
    logger.info(f"Iniciando tarea de recuperación: {task_id}")
    
    # Si está autorizado, llamar al servicio de recuperación de datos
    try:
        response = await start_retrieval_task(task_id)
        logger.info(f"Tarea iniciada con éxito: {task_id}")
        return response
    except Exception as e:
        logger.error(f"Error al iniciar tarea {task_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error de comunicación con el servicio: {str(e)}")

@router.post("/data-retrieval/tasks/{task_id}/images")
async def api_upload_image(
    task_id: str,
    file: UploadFile = File(...),
    format: str = Form(...),
    modality: str = Form(...),
    region: str = Form(...),
    dimensions: Optional[str] = Form(None)
):
    """
    Endpoint para subir una imagen a una tarea.
    Primero verifica autorización con el servicio auth y luego reenvía al servicio data-retrieval.
    """
    # Verificar autorización
    is_authorized = await verify_authorization()
    if not is_authorized:
        logger.warning(f"Intento de acceso no autorizado al subir imagen para tarea {task_id}")
        raise HTTPException(status_code=401, detail="No autorizado para acceder a este recurso")
    
    logger.info(f"Subiendo imagen para tarea: {task_id}")
    
    # Si está autorizado, llamar al servicio de recuperación de datos
    try:
        # Leer el contenido del archivo
        file_content = await file.read()
        
        response = await upload_image_to_task(
            task_id=task_id, 
            file=file,
            file_content=file_content,
            format=format,
            modality=modality,
            region=region,
            dimensions=dimensions
        )
        
        logger.info(f"Imagen subida con éxito para tarea {task_id}")
        return response
    except Exception as e:
        logger.error(f"Error al subir imagen para tarea {task_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error de comunicación con el servicio: {str(e)}")