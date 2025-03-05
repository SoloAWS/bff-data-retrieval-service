import os
from typing import Optional, Dict
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Cargar variables de entorno desde archivo .env
load_dotenv()

class Settings(BaseSettings):
    """Configuración para el servicio BFF"""
    
    # Configuración general
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = environment == "development"
    port: int = int(os.getenv("PORT", "8080"))
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    # URLs de los servicios
    auth_service_url: str = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8080")
    data_retrieval_service_url: str = os.getenv(
        "DATA_RETRIEVAL_SERVICE_URL", "http://data-retrieval-service:8000"
    )
    
    # Token de autenticación (quemado para el ejemplo)
    auth_token: str = os.getenv(
        "AUTH_TOKEN", 
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkRhdGFQYXJ0bmVyIn0.BnLA0KJC3-fQBzpK0KfSO0p4s-KUEHNlpdvUx0Qkzsk"
    )
    
    # Configuración de Pulsar
    pulsar_service_url: str = os.getenv("PULSAR_SERVICE_URL", "pulsar://pulsar-broker:6650")
    pulsar_token: str = os.getenv("PULSAR_TOKEN", "")
    pulsar_client_config: Dict = {}
    
    # Mapeo de comandos a tópicos de Pulsar
    pulsar_topics_mapping: Dict[str, str] = {
        "CreateRetrievalTask": "persistent://public/default/data-retrieval-commands",
        "StartRetrievalTask": "persistent://public/default/data-retrieval-commands",
        "UploadImage": "persistent://public/default/data-retrieval-commands"
    }
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

# Instancia única de configuración
settings = Settings()