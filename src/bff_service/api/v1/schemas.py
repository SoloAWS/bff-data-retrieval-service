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
    task_id: str
    batch_id: str
    source: str
    status: str
    message: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    total_images: Optional[int] = None
    successful_images: Optional[int] = None
    failed_images: Optional[int] = None
    images_count: Optional[int] = None


class ImageInfo(BaseModel):
    """Schema for image information"""
    image_id: str
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


class ImageUploadResponse(BaseModel):
    """Response schema for image upload"""
    task_id: str
    image_id: str
    filename: str
    modality: str
    region: str
    size_bytes: int