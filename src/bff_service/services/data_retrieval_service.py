import logging
import httpx
import uuid
from typing import Dict, Any, Optional, List
from fastapi import UploadFile

from ..core.config import settings
from ..services.messaging.pulsar_publisher import PulsarPublisher

logger = logging.getLogger(__name__)

# Clase para gestionar servicios de recuperación de datos
class DataRetrievalService:
    def __init__(self, pulsar_publisher: Optional[PulsarPublisher] = None):
        """
        Inicializa el servicio de recuperación de datos.
        
        Args:
            pulsar_publisher: Instancia del publicador de Pulsar para enviar comandos
        """
        self.service_url = settings.data_retrieval_service_url
        self.pulsar_publisher = pulsar_publisher
    
    async def create_retrieval_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Envía un comando para crear una nueva tarea de recuperación.
        
        Args:
            task_data: Datos de la tarea a crear
            
        Returns:
            Dict: Respuesta del comando
            
        Raises:
            Exception: Si hay un error en la comunicación
        """
        if not self.pulsar_publisher:
            # Si no hay publicador de Pulsar, usar HTTP como fallback
            return await self._create_retrieval_task_http(task_data)
        
        try:
            # Publicar comando via Pulsar
            response = await self.pulsar_publisher.publish_command(
                command_type="CreateRetrievalTask",
                data=task_data
            )
            
            # Añadir información de la tarea a la respuesta
            response["task_id"] = str(uuid.uuid4())  # ID temporal hasta que el servicio procese el comando
            response["batch_id"] = task_data.get("batch_id", "")
            response["source"] = task_data.get("source_name", "")
            response["status"] = "PENDING"
            
            return response
        except Exception as e:
            logger.error(f"Error al publicar comando CreateRetrievalTask: {str(e)}")
            # Intentar fallback a HTTP
            return await self._create_retrieval_task_http(task_data)
    
    async def _create_retrieval_task_http(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fallback: Llama al servicio de recuperación de datos via HTTP para crear una tarea.
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.service_url}/api/v1/data-retrieval/tasks",
                    json=task_data,
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
    
    async def start_retrieval_task(self, task_id: str) -> Dict[str, Any]:
        """
        Envía un comando para iniciar una tarea existente.
        
        Args:
            task_id: ID de la tarea a iniciar
            
        Returns:
            Dict: Respuesta del comando
            
        Raises:
            Exception: Si hay un error en la comunicación
        """
        if not self.pulsar_publisher:
            # Si no hay publicador de Pulsar, usar HTTP como fallback
            return await self._start_retrieval_task_http(task_id)
        
        try:
            # Publicar comando via Pulsar
            data = {"task_id": task_id}
            response = await self.pulsar_publisher.publish_command(
                command_type="StartRetrievalTask",
                data=data
            )
            
            # Añadir información de la tarea a la respuesta
            task_info = await self.get_retrieval_task(task_id)
            if task_info:
                response.update({
                    "task_id": task_id,
                    "batch_id": task_info.get("batch_id", ""),
                    "source": task_info.get("source_name", ""),
                    "status": "IN_PROGRESS"
                })
            else:
                response.update({
                    "task_id": task_id,
                    "status": "IN_PROGRESS"
                })
            
            return response
        except Exception as e:
            logger.error(f"Error al publicar comando StartRetrievalTask: {str(e)}")
            # Intentar fallback a HTTP
            return await self._start_retrieval_task_http(task_id)
    
    async def _start_retrieval_task_http(self, task_id: str) -> Dict[str, Any]:
        """
        Fallback: Llama al servicio de recuperación de datos via HTTP para iniciar una tarea.
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.service_url}/api/v1/data-retrieval/tasks/{task_id}/start",
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
        self,
        task_id: str,
        file: UploadFile,
        file_content: bytes,
        format: str,
        modality: str,
        region: str,
        dimensions: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Sube una imagen a una tarea usando HTTP (no es posible enviar archivos via Pulsar).
        
        Args:
            task_id: ID de la tarea
            file: Objeto UploadFile con el archivo a subir
            file_content: Contenido del archivo en bytes
            format: Formato de la imagen
            modality: Modalidad de la imagen
            region: Región de la imagen
            dimensions: Dimensiones de la imagen (opcional)
            
        Returns:
            Dict: Respuesta del servicio
            
        Raises:
            Exception: Si hay un error en la comunicación
        """
        # Para subir archivos, siempre usar HTTP
        return await self._upload_image_to_task_http(
            task_id, file, file_content, format, modality, region, dimensions
        )
    
    async def _upload_image_to_task_http(
        self,
        task_id: str,
        file: UploadFile,
        file_content: bytes,
        format: str,
        modality: str,
        region: str,
        dimensions: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Llama al servicio de recuperación de datos via HTTP para subir una imagen.
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
                    f"{self.service_url}/api/v1/data-retrieval/tasks/{task_id}/images",
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
    
    async def get_retrieval_task(self, task_id: str) -> Dict[str, Any]:
        """
        Obtiene información de una tarea usando HTTP (las consultas siempre son via HTTP).
        
        Args:
            task_id: ID de la tarea
            
        Returns:
            Dict: Información de la tarea
            
        Raises:
            Exception: Si hay un error en la comunicación
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.service_url}/api/v1/data-retrieval/tasks/{task_id}",
                    timeout=30.0
                )
                
                # Verificar si la respuesta es exitosa
                response.raise_for_status()
                
                # Devolver la respuesta del servicio tal cual
                # No transformamos los datos para mantener la estructura original
                return response.json()
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    return None
                logger.error(f"Error HTTP del servicio de recuperación: {e.response.status_code} - {e.response.text}")
                raise Exception(f"Error del servicio de recuperación: {e.response.status_code} - {e.response.text}")
            except Exception as e:
                logger.error(f"Error al comunicarse con el servicio de recuperación: {str(e)}")
                raise
    
    async def get_task_images(self, task_id: str) -> List[Dict[str, Any]]:
        """
        Obtiene las imágenes de una tarea usando HTTP.
        
        Args:
            task_id: ID de la tarea
            
        Returns:
            List: Lista de imágenes
            
        Raises:
            Exception: Si hay un error en la comunicación
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.service_url}/api/v1/data-retrieval/tasks/{task_id}/images",
                    timeout=30.0
                )
                
                # Verificar si la respuesta es exitosa
                response.raise_for_status()
                
                # Devolver la respuesta del servicio tal cual
                # No transformamos los datos para mantener la estructura original
                return response.json()
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    return []
                logger.error(f"Error HTTP del servicio de recuperación: {e.response.status_code} - {e.response.text}")
                raise Exception(f"Error del servicio de recuperación: {e.response.status_code} - {e.response.text}")
            except Exception as e:
                logger.error(f"Error al comunicarse con el servicio de recuperación: {str(e)}")
                raise
    
    async def get_tasks_by_filters(
        self, 
        source_id: Optional[str] = None,
        batch_id: Optional[str] = None,
        pending_only: bool = False,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Obtiene tareas según filtros usando HTTP.
        
        Args:
            source_id: ID de la fuente
            batch_id: ID del lote
            pending_only: Solo tareas pendientes
            limit: Límite de resultados
            
        Returns:
            List: Lista de tareas
            
        Raises:
            Exception: Si hay un error en la comunicación
        """
        async with httpx.AsyncClient() as client:
            try:
                params = {}
                if source_id:
                    params["source_id"] = source_id
                if batch_id:
                    params["batch_id"] = batch_id
                if pending_only:
                    params["pending_only"] = "true"
                params["limit"] = str(limit)
                
                response = await client.get(
                    f"{self.service_url}/api/v1/data-retrieval/tasks",
                    params=params,
                    timeout=30.0
                )
                
                # Verificar si la respuesta es exitosa
                response.raise_for_status()
                
                # Devolver la respuesta del servicio tal cual
                # No transformamos los datos para mantener la estructura original 
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"Error HTTP del servicio de recuperación: {e.response.status_code} - {e.response.text}")
                raise Exception(f"Error del servicio de recuperación: {e.response.status_code} - {e.response.text}")
            except Exception as e:
                logger.error(f"Error al comunicarse con el servicio de recuperación: {str(e)}")
                raise