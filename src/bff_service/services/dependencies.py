import logging
from typing import Optional

from .messaging.pulsar_publisher import PulsarPublisher
from ..core.config import settings

logger = logging.getLogger(__name__)

# Variable global para guardar el publicador de Pulsar
_pulsar_publisher_instance = None

def initialize_pulsar_publisher() -> Optional[PulsarPublisher]:
    """
    Inicializa el publicador de Pulsar.
    
    Returns:
        PulsarPublisher: Instancia del publicador o None si hay error
    """
    global _pulsar_publisher_instance
    
    try:
        # Inicializar el publicador de Pulsar
        if settings.pulsar_service_url:
            _pulsar_publisher_instance = PulsarPublisher(
                service_url=settings.pulsar_service_url,
                topics_mapping=settings.pulsar_topics_mapping,
                token=settings.pulsar_token,
                client_config=settings.pulsar_client_config
            )
            logger.info("Pulsar publisher initialized successfully")
        else:
            logger.warning("Pulsar service URL not configured, messaging disabled")
    except Exception as e:
        logger.error(f"Error initializing Pulsar publisher: {str(e)}")
        logger.warning("Continuing without Pulsar messaging")
    
    return _pulsar_publisher_instance

def get_pulsar_publisher() -> Optional[PulsarPublisher]:
    """
    Obtiene la instancia del publicador de Pulsar.
    
    Returns:
        PulsarPublisher: Instancia del publicador o None si no está inicializado
    """
    return _pulsar_publisher_instance

def close_pulsar_publisher() -> None:
    """
    Cierra la instancia del publicador de Pulsar.
    """
    global _pulsar_publisher_instance
    
    if _pulsar_publisher_instance:
        try:
            _pulsar_publisher_instance.close()
            logger.info("Pulsar publisher closed successfully")
        except Exception as e:
            logger.error(f"Error closing Pulsar publisher: {str(e)}")
        
        _pulsar_publisher_instance = None