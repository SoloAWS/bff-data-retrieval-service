import logging
import httpx
from typing import Optional
from ..core.config import settings

logger = logging.getLogger(__name__)


async def verify_authorization(authorization: Optional[str] = None) -> bool:
    """
    Verifica la autorización llamando al servicio de autenticación.

    Args:
        authorization: Token de autorización tomado del encabezado de la petición

    Returns:
        bool: True si está autorizado, False en caso contrario
    """
    if not authorization:
        logger.error("Token de autenticación no proporcionado en los encabezados")
        return False

    async with httpx.AsyncClient() as client:
        try:
            # Llamar al servicio de autenticación
            headers = {"Authorization": authorization}

            logger.debug(
                f"Verificando autorización con {settings.auth_service_url}/auth"
            )
            response = await client.post(
                f"{settings.auth_service_url}/auth", headers=headers, timeout=10.0
            )

            # Comprobar explícitamente el código de respuesta
            if response.status_code == 200:
                logger.debug("Autorización exitosa")
                return True
            else:
                logger.warning(
                    f"Autorización fallida: {response.status_code} - {response.text}"
                )
                return False

        except httpx.HTTPStatusError as e:
            logger.error(
                f"Error HTTP del servicio de autenticación: {e.response.status_code} - {e.response.text}"
            )
            return False
        except httpx.RequestError as e:
            logger.error(
                f"Error de conexión con el servicio de autenticación: {str(e)}"
            )
            return False
        except Exception as e:
            logger.error(
                f"Error inesperado al comunicarse con el servicio de autenticación: {str(e)}"
            )
            # En caso de error, negamos la autorización por seguridad
            return False
