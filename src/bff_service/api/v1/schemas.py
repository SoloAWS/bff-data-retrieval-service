from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from enum import Enum


class SourceTypeEnum(str, Enum):
    HOSPITAL = "HOSPITAL"
    LABORATORY = "LABORATORY"
    CLINIC = "CLINIC"
    RESEARCH_CENTER = "RESEARCH_CENTER"


class RetrievalMethodEnum(str, Enum):
    SFTP = "SFTP"
    API = "API"
    DIRECT_UPLOAD = "DIRECT_UPLOAD"
    CLOUD_STORAGE = "CLOUD_STORAGE"


class ImageFormatEnum(str, Enum):
    DICOM = "DICOM"
    JPEG = "JPEG"
    PNG = "PNG"
    TIFF = "TIFF"
    RAW = "RAW"


class CreateTaskRequest(BaseModel):
    """Schema for creating a data retrieval task"""
    source_type: SourceTypeEnum
    source_name: str
    source_id: str
    location: str
    retrieval_method: RetrievalMethodEnum
    batch_id: str
    priority: int = 0
    metadata: Optional[Dict[str, Any]] = None


class CommandResponse(BaseModel):
    """Generic response for commands sent via Pulsar"""
    command_id: str
    correlation_id: str
    topic: str
    message_id: str
    status: str


class TaskResponse(BaseModel):
    """Response schema for task information"""
    id: str
    batch_id: str
    source_type: str
    source_name: str
    source_id: str
    location: str
    retrieval_method: str
    priority: int
    storage_path: str
    status: str
    message: Optional[str] = None
    total_images: int = 0
    successful_images: int = 0
    failed_images: int = 0
    details: Optional[Dict[str, Any]] = None
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    images_count: int = 0
    result: Optional[Dict[str, Any]] = None
    
    class Config:
        # Allow extra fields in case API response contains additional data
        extra = "ignore"


class ImageInfo(BaseModel):
    """Schema for image information"""
    id: str
    task_id: str
    filename: str
    file_path: str
    format: str
    modality: str
    region: str
    size_bytes: int
    dimensions: Optional[str] = None
    is_stored: bool = False
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    class Config:
        # Allow extra fields in case API response contains additional data
        extra = "ignore"


class ImageUploadResponse(BaseModel):
    """Response schema for image upload"""
    task_id: str
    image_id: str
    filename: str
    file_path: str
    modality: str
    region: str
    size_bytes: int
    
    class Config:
        # Allow extra fields in case API response contains additional data
        extra = "ignore"