import logging
import httpx
from typing import Dict, Any, Optional
from fastapi import UploadFile

from ..core.config import settings

logger = logging.getLogger(__name__)

async def create_retrieval_task(task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Llama al servicio de recuperación de datos para crear una nueva tarea.
    
    Args:
        task_data: Datos de la tarea a crear
        
    Returns:
        Dict: Respuesta del servicio de recuperación
        
    Raises:
        Exception: Si hay un error en la comunicación con el servicio
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{settings.data_retrieval_service_url}/api/v1/data-retrieval/tasks",
                json=task_data.dict() if hasattr(task_data, 'dict') else task_data,
                timeout=30.0
            )
            
            # Verificar si la respuesta es exitosa
            response.raise_for_status()
            
            # Devolver la respuesta del servicio
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Error HTTP del servicio de recuperación: {settings.data_retrieval_service_url} {e.response.status_code} - {e.response.text}")
            raise Exception(f"Error del servicio de recuperación: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            logger.error(f"Error al comunicarse con el servicio de recuperación: {str(e)}")
            raise

async def start_retrieval_task(task_id: str) -> Dict[str, Any]:
    """
    Llama al servicio de recuperación de datos para iniciar una tarea existente.
    
    Args:
        task_id: ID de la tarea a iniciar
        
    Returns:
        Dict: Respuesta del servicio de recuperación
        
    Raises:
        Exception: Si hay un error en la comunicación con el servicio
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{settings.data_retrieval_service_url}/api/v1/data-retrieval/tasks/{task_id}/start",
                json={},
                timeout=30.0
            )
            
            # Verificar si la respuesta es exitosa
            response.raise_for_status()
            
            # Devolver la respuesta del servicio
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Error HTTP del servicio de recuperación: {e.response.status_code} - {e.response.text}")
            raise Exception(f"Error del servicio de recuperación: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            logger.error(f"Error al comunicarse con el servicio de recuperación: {str(e)}")
            raise

async def upload_image_to_task(
    task_id: str,
    file: UploadFile,
    file_content: bytes,
    format: str,
    modality: str,
    region: str,
    dimensions: Optional[str] = None
) -> Dict[str, Any]:
    """
    Llama al servicio de recuperación de datos para subir una imagen a una tarea.
    
    Args:
        task_id: ID de la tarea
        file: Objeto UploadFile con el archivo a subir
        file_content: Contenido del archivo en bytes
        format: Formato de la imagen
        modality: Modalidad de la imagen
        region: Región de la imagen
        dimensions: Dimensiones de la imagen (opcional)
        
    Returns:
        Dict: Respuesta del servicio de recuperación
        
    Raises:
        Exception: Si hay un error en la comunicación con el servicio
    """
    async with httpx.AsyncClient() as client:
        try:
            # Preparar los datos para la solicitud multipart
            files = {"file": (file.filename, file_content, file.content_type)}
            data = {
                "format": format,
                "modality": modality,
                "region": region
            }
            
            if dimensions:
                data["dimensions"] = dimensions
            
            response = await client.post(
                f"{settings.data_retrieval_service_url}/api/v1/data-retrieval/tasks/{task_id}/images",
                files=files,
                data=data,
                timeout=60.0  # Timeout más largo para subida de archivos
            )
            
            # Verificar si la respuesta es exitosa
            response.raise_for_status()
            
            # Devolver la respuesta del servicio
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Error HTTP del servicio de recuperación: {e.response.status_code} - {e.response.text}")
            raise Exception(f"Error del servicio de recuperación: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            logger.error(f"Error al comunicarse con el servicio de recuperación: {str(e)}")
            raise