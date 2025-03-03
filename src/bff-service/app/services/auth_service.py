import logging
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)

async def verify_authorization() -> bool:
    """
    Verifica la autorización con el servicio de autenticación existente.
    
    Returns:
        bool: True si la autenticación es exitosa, False en caso contrario
    """
    async with httpx.AsyncClient() as client:
        try:
            logger.debug(f"Verificando autorización con {settings.auth_service_url}/auth")
            
            headers = {"Authorization": f"Bearer {settings.auth_token}"}
            response = await client.post(
                f"{settings.auth_service_url}/auth", 
                headers=headers,
                timeout=10.0  # Timeout en segundos
            )
            
            if response.status_code == 200:
                auth_data = response.json()
                # Suponemos que el servicio de auth devuelve un campo "authorized" booleano
                is_authorized = auth_data.get("authorized", False)
                logger.info(f"Resultado de autenticación: {'Autorizado' if is_authorized else 'No autorizado'}")
                return is_authorized
            else:
                logger.error(f"Error de autenticación: {response.status_code} - {response.text}")
                return False
                
        except httpx.ConnectError:
            logger.error(f"No se pudo conectar al servicio de autenticación: {settings.auth_service_url}")
            return False
        except httpx.TimeoutException:
            logger.error("Timeout al conectar con el servicio de autenticación")
            return False
        except Exception as e:
            logger.error(f"Error al comunicarse con el servicio de autenticación: {str(e)}")
            return False