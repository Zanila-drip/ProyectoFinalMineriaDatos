from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class VideoUpload(BaseModel):
    camera_id: str
    filename: str
    created_at: datetime
    status: str = "pending"

class VideoResponse(BaseModel):
    id: str
    camera_id: str
    filename: str
    created_at: datetime
    status: str
    processing_time: Optional[float] = None
    detections: Optional[List[dict]] = None

class TestResult(BaseModel):
    video_id: str
    camera_id: str
    start_time: datetime
    end_time: Optional[datetime]
    status: str
    results: Optional[dict]

class DetectionResult(BaseModel):
    frame_number: int
    timestamp: datetime
    detections: List[dict]
    processing_time: float 