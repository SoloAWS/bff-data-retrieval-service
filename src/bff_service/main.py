import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .api import api_router
from .services.dependencies import (
    initialize_pulsar_publisher,
    close_pulsar_publisher,
    get_pulsar_publisher
)

# Configurar logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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
    # Inicializar el publicador de Pulsar
    initialize_pulsar_publisher()

@app.on_event("shutdown")
async def shutdown_event():
    """Limpia recursos al cerrar la aplicación"""
    # Cerrar el publicador de Pulsar
    close_pulsar_publisher()

# Hacer accesible el getter desde otros módulos
__all__ = ['app', 'get_pulsar_publisher']

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.debug
    )