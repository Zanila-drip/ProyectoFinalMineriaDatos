from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from typing import List
from datetime import datetime
from ..models import VideoUpload, VideoResponse, TestResult, DetectionResult
from ..services.video_service import VideoService
import httpx
import os

router = APIRouter()
video_service = VideoService()

# URLs de las APIs de cámaras
CAMERA_APIS = {
    "cam1": "http://api-cam1:8000",
    "cam2": "http://api-cam2:8000",
    "cam3": "http://api-cam3:8000",
    "cam4": "http://api-cam4:8000"
}

@router.post("/upload/{camera_id}")
async def upload_video(camera_id: str, video: UploadFile = File(...)):
    """Sube un video a la API de la cámara correspondiente"""
    if camera_id not in CAMERA_APIS:
        raise HTTPException(status_code=400, detail="ID de cámara no válido")
    
    # Obtener la URL de la API de la cámara
    camera_api_url = CAMERA_APIS[camera_id]
    
    # Reenviar el video a la API de la cámara
    async with httpx.AsyncClient() as client:
        files = {"video": (video.filename, video.file, video.content_type)}
        response = await client.post(
            f"{camera_api_url}/api/v1/videos/upload/{camera_id}",
            files=files
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail="Error al subir el video a la API de la cámara"
            )
        
        return response.json()

@router.get("/videos", response_model=List[VideoResponse])
async def get_videos():
    """Obtiene todos los videos de todas las cámaras"""
    videos = video_service.get_videos()
    return [
        VideoResponse(
            id=video["filename"],
            camera_id=video["filename"].split("_")[1],
            filename=video["filename"],
            created_at=video["created_at"],
            status=video_service.get_video_status(video["filename"])["status"] 
            if video_service.get_video_status(video["filename"]) 
            else "pending"
        )
        for video in videos
    ]

@router.post("/status/{filename}")
async def update_video_status(filename: str, status: dict):
    """Actualiza el estado de un video en la API de la cámara correspondiente"""
    # Determinar a qué cámara pertenece el video
    camera_id = None
    for cam_id in CAMERA_APIS:
        if filename.startswith(f"{cam_id}_"):
            camera_id = cam_id
            break
    
    if not camera_id:
        raise HTTPException(status_code=404, detail="Video no encontrado")
    
    # Actualizar estado en la API de la cámara
    camera_api_url = CAMERA_APIS[camera_id]
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{camera_api_url}/api/v1/videos/status/{filename}",
            json=status
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail="Error al actualizar el estado del video"
            )
        
        return response.json()

@router.get("/video/{filename}", response_model=VideoResponse)
async def get_video(filename: str):
    video_path = video_service.get_video_path(filename)
    if not video_path:
        raise HTTPException(status_code=404, detail="Video no encontrado")
    
    status = video_service.get_video_status(filename)
    if not status:
        status = {"status": "pending"}
    
    return VideoResponse(
        id=filename,
        camera_id=filename.split("_")[1],
        filename=filename,
        created_at=datetime.fromtimestamp(video_path.stat().st_ctime),
        status=status["status"]
    )

@router.post("/test/start", response_model=TestResult)
async def start_test():
    # Implementación pendiente
    return TestResult(
        video_id="test_1",
        camera_id="cam1",
        start_time=datetime.now(),
        status="running"
    )

@router.get("/test/results/{test_id}", response_model=TestResult)
async def get_test_results(test_id: str):
    # Implementación pendiente
    return TestResult(
        video_id=test_id,
        camera_id="cam1",
        start_time=datetime.now(),
        status="completed"
    ) 