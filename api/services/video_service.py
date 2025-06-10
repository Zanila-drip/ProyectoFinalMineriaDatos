from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path
import redis
import json
from .video_processor import VideoProcessor

class VideoService:
    def __init__(self, camera_id: str = 'cam1'):
        self.camera_id = camera_id
        self.videos_dir = Path("videos")
        self.videos_dir.mkdir(exist_ok=True)
        self.redis_client = redis.Redis(host='redis', port=6379, db=0)
        self.processor = VideoProcessor(camera_id)

    def get_videos(self) -> List[Dict]:
        """Obtiene todos los videos"""
        return self.processor.get_pending_videos()

    def get_video_path(self, filename: str) -> Optional[Path]:
        """Obtiene la ruta del video si existe"""
        video_path = self.videos_dir / filename
        return video_path if video_path.exists() else None

    def get_video_status(self, filename: str) -> Optional[Dict]:
        """Obtiene el estado de un video"""
        return self.processor.get_video_status(filename)

    def update_video_status(self, filename: str, status: Dict) -> None:
        """Actualiza el estado del video en Redis"""
        self.redis_client.set(
            f"video_status:{filename}",
            json.dumps(status)
        )

    def save_video(self, video_file, filename: str) -> str:
        """Guarda un video subido y lo marca como pendiente"""
        video_path = self.videos_dir / filename
        with open(video_path, "wb") as f:
            f.write(video_file.read())
        return str(video_path)

    def process_video(self, filename: str) -> Dict:
        """Procesa un video usando el VideoProcessor"""
        video_path = self.videos_dir / filename
        if not video_path.exists():
            raise FileNotFoundError(f"Video no encontrado: {filename}")
        return self.processor.process_video(str(video_path))