import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .api import api_router
from .services.messaging.pulsar_publisher import PulsarPublisher

# Configurar logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Instancia global del publicador de Pulsar
pulsar_publisher = None

# Crear la aplicación FastAPI
app = FastAPI(
    title="Medical Imaging BFF Service",
    description="Backend For Frontend para servicios de imágenes médicas",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rutas
app.include_router(api_router, prefix="/api/bff")

# Endpoint de health check
@app.get("/health", tags=["health"])
async def health_check():
    """Endpoint para verificar el estado del servicio BFF"""
    return {
        "status": "ok",
        "service": "medical-imaging-bff",
        "version": "1.0.0",
        "environment": settings.environment
    }

# Eventos de inicio y cierre de la aplicación
@app.on_event("startup")
async def startup_event():
    """Inicializa recursos al iniciar la aplicación"""
    global pulsar_publisher
    
    try:
        # Inicializar el publicador de Pulsar
        if settings.pulsar_service_url:
            pulsar_publisher = PulsarPublisher(
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

@app.on_event("shutdown")
async def shutdown_event():
    """Limpia recursos al cerrar la aplicación"""
    global pulsar_publisher
    
    if pulsar_publisher:
        try:
            pulsar_publisher.close()
            logger.info("Pulsar publisher closed successfully")
        except Exception as e:
            logger.error(f"Error closing Pulsar publisher: {str(e)}")

# Dependency to get pulsar publisher
def get_pulsar_publisher():
    """Returns the Pulsar publisher instance"""
    return pulsar_publisher

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.debug
    )