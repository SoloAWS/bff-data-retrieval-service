import logging
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends, Header, Query
from typing import Dict, Any, Optional, List
from pydantic import BaseModel

from ...services.auth_service import verify_authorization
from ...services.data_retrieval_service import DataRetrievalService
from ...services.dependencies import get_pulsar_publisher
from .schemas import (
    CreateTaskRequest, 
    CommandResponse, 
    TaskResponse, 
    ImageInfo, 
    ImageUploadResponse
)

# Configurar logging
logger = logging.getLogger(__name__)

# Crear router
router = APIRouter(prefix="/data-retrieval")

# Endpoints

@router.post("/tasks", status_code=203, response_model=CommandResponse)
async def api_create_task(
    request: CreateTaskRequest,
    authorization: str = Header(None),
    pulsar_publisher = Depends(get_pulsar_publisher)
):
    """
    Endpoint para crear una tarea de recuperación de imágenes.
    Primero verifica autorización con el servicio auth y luego envía
    un comando via Pulsar al servicio data-retrieval.
    """
    # Verificar autorización
    is_authorized = await verify_authorization(authorization)
    if not is_authorized:
        logger.warning("Intento de acceso no autorizado al crear tarea")
        raise HTTPException(status_code=401, detail="No autorizado para acceder a este recurso")
    
    logger.info(f"Creando tarea de recuperación para {request.source_name}")
    
    # Inicializar servicio
    data_retrieval_service = DataRetrievalService(pulsar_publisher)
    
    # Crear tarea usando el servicio
    try:
        response = await data_retrieval_service.create_retrieval_task(request.dict())
        logger.info(f"Comando de creación de tarea enviado con éxito. ID: {response.get('task_id', 'N/A')}")
        return response
    except Exception as e:
        logger.error(f"Error al crear tarea: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error de comunicación con el servicio: {str(e)}")


@router.post("/tasks/{task_id}/start", status_code=203)
async def api_start_task(
    task_id: str,
    authorization: str = Header(None),
    pulsar_publisher = Depends(get_pulsar_publisher)
):
    """
    Endpoint para iniciar una tarea de recuperación.
    Primero verifica autorización con el servicio auth y luego envía
    un comando via Pulsar al servicio data-retrieval.
    """
    # Verificar autorización
    is_authorized = await verify_authorization(authorization)
    if not is_authorized:
        logger.warning(f"Intento de acceso no autorizado al iniciar tarea {task_id}")
        raise HTTPException(status_code=401, detail="No autorizado para acceder a este recurso")
    
    logger.info(f"Iniciando tarea de recuperación: {task_id}")
    
    # Inicializar servicio
    data_retrieval_service = DataRetrievalService(pulsar_publisher)
    
    # Iniciar tarea usando el servicio
    try:
        response = await data_retrieval_service.start_retrieval_task(task_id)
        logger.info(f"Comando de inicio de tarea enviado con éxito: {task_id}")
        return f"Comando de inicio de tarea enviado con éxito: {task_id}" if response else "Error al enviar comando de inicio de tarea"
    except Exception as e:
        logger.error(f"Error al iniciar tarea {task_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error de comunicación con el servicio: {str(e)}")

@router.post("/tasks/{task_id}/images", status_code=203, response_model=ImageUploadResponse)
async def api_upload_image(
    task_id: str,
    file: UploadFile = File(...),
    format: str = Form(...),
    modality: str = Form(...),
    region: str = Form(...),
    dimensions: Optional[str] = Form(None),
    authorization: str = Header(None),
    pulsar_publisher = Depends(get_pulsar_publisher)
):
    """
    Endpoint para subir una imagen a una tarea.
    Primero verifica autorización con el servicio auth y luego
    reenvía directamente al servicio data-retrieval (no usa Pulsar).
    """
    # Verificar autorización
    is_authorized = await verify_authorization(authorization)
    if not is_authorized:
        logger.warning(f"Intento de acceso no autorizado al subir imagen para tarea {task_id}")
        raise HTTPException(status_code=401, detail="No autorizado para acceder a este recurso")
    
    logger.info(f"Subiendo imagen para tarea: {task_id}")
    
    # Inicializar servicio
    data_retrieval_service = DataRetrievalService(pulsar_publisher)
    
    # Subir imagen usando el servicio
    try:
        # Leer el contenido del archivo
        file_content = await file.read()
        
        response = await data_retrieval_service.upload_image_to_task(
            task_id=task_id, 
            file=file,
            file_content=file_content,
            format=format,
            modality=modality,
            region=region,
            dimensions=dimensions
        )
        
        logger.info(f"Imagen subida con éxito para tarea {task_id}")
        # Devolvemos la respuesta directamente, con la estructura original
        return response
    except Exception as e:
        logger.error(f"Error al subir imagen para tarea {task_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error de comunicación con el servicio: {str(e)}")

@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def api_get_task(
    task_id: str,
    authorization: str = Header(None),
    pulsar_publisher = Depends(get_pulsar_publisher)
):
    """
    Endpoint para obtener información de una tarea.
    Primero verifica autorización con el servicio auth y luego
    consulta directamente al servicio data-retrieval.
    """
    # Verificar autorización
    is_authorized = await verify_authorization(authorization)
    if not is_authorized:
        logger.warning(f"Intento de acceso no autorizado al obtener tarea {task_id}")
        raise HTTPException(status_code=401, detail="No autorizado para acceder a este recurso")
    
    logger.info(f"Obteniendo información de tarea: {task_id}")
    
    # Inicializar servicio
    data_retrieval_service = DataRetrievalService(pulsar_publisher)
    
    # Obtener tarea usando el servicio
    try:
        task = await data_retrieval_service.get_retrieval_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail=f"No se encontró la tarea con ID {task_id}")
        
        logger.info(f"Información de tarea obtenida con éxito: {task_id}")
        # Devolver la respuesta directamente, sin modificar su estructura
        return task
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener información de tarea {task_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error de comunicación con el servicio: {str(e)}")

@router.get("/tasks/{task_id}/images", response_model=List[ImageInfo])
async def api_get_task_images(
    task_id: str,
    authorization: str = Header(None),
    pulsar_publisher = Depends(get_pulsar_publisher)
):
    """
    Endpoint para obtener las imágenes de una tarea.
    Primero verifica autorización con el servicio auth y luego
    consulta directamente al servicio data-retrieval.
    """
    # Verificar autorización
    is_authorized = await verify_authorization(authorization)
    if not is_authorized:
        logger.warning(f"Intento de acceso no autorizado al obtener imágenes de tarea {task_id}")
        raise HTTPException(status_code=401, detail="No autorizado para acceder a este recurso")
    
    logger.info(f"Obteniendo imágenes de tarea: {task_id}")
    
    # Inicializar servicio
    data_retrieval_service = DataRetrievalService(pulsar_publisher)
    
    # Obtener imágenes usando el servicio
    try:
        images = await data_retrieval_service.get_task_images(task_id)
        logger.info(f"Imágenes obtenidas con éxito para tarea {task_id}: {len(images)} imágenes")
        # Devolver las imágenes directamente, sin modificar su estructura
        return images
    except Exception as e:
        logger.error(f"Error al obtener imágenes de tarea {task_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error de comunicación con el servicio: {str(e)}")

@router.get("/tasks", response_model=List[TaskResponse])
async def api_get_tasks(
    source_id: Optional[str] = Query(None),
    batch_id: Optional[str] = Query(None),
    pending_only: bool = Query(False),
    limit: int = Query(10, gt=0, le=100),
    authorization: str = Header(None),
    pulsar_publisher = Depends(get_pulsar_publisher)
):
    """
    Endpoint para obtener tareas filtradas.
    Primero verifica autorización con el servicio auth y luego
    consulta directamente al servicio data-retrieval.
    """
    # Verificar autorización
    is_authorized = await verify_authorization(authorization)
    if not is_authorized:
        logger.warning("Intento de acceso no autorizado al obtener tareas")
        raise HTTPException(status_code=401, detail="No autorizado para acceder a este recurso")
    
    # Verificar parámetros
    if not any([source_id, batch_id, pending_only]):
        raise HTTPException(status_code=400, detail="Se requiere al menos un filtro: source_id, batch_id o pending_only")
    
    logger.info(f"Obteniendo tareas filtradas: source_id={source_id}, batch_id={batch_id}, pending_only={pending_only}")
    
    # Inicializar servicio
    data_retrieval_service = DataRetrievalService(pulsar_publisher)
    
    # Obtener tareas usando el servicio
    try:
        tasks = await data_retrieval_service.get_tasks_by_filters(
            source_id=source_id,
            batch_id=batch_id,
            pending_only=pending_only,
            limit=limit
        )
        logger.info(f"Tareas obtenidas con éxito: {len(tasks)} tareas")
        # Devolver las tareas directamente, sin modificar su estructura
        return tasks
    except Exception as e:
        logger.error(f"Error al obtener tareas: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error de comunicación con el servicio: {str(e)}")