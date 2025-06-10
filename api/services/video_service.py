from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path
import redis
import json

class VideoService:
    def __init__(self):
        self.videos_dir = Path("videos")
        self.videos_dir.mkdir(exist_ok=True)
        self.redis_client = redis.Redis(host='redis', port=6379, db=0)

    def get_videos(self) -> List[Dict]:
        """Obtiene la lista de videos disponibles"""
        videos = []
        for video_file in self.videos_dir.glob("*"):
            if video_file.is_file():
                videos.append({
                    "filename": video_file.name,
                    "created_at": datetime.fromtimestamp(video_file.stat().st_ctime)
                })
        return videos

    def get_video_path(self, filename: str) -> Optional[Path]:
        """Obtiene la ruta del video si existe"""
        video_path = self.videos_dir / filename
        return video_path if video_path.exists() else None

    def get_video_status(self, filename: str) -> Optional[Dict]:
        """Obtiene el estado del video desde Redis"""
        status = self.redis_client.get(f"video_status:{filename}")
        return json.loads(status) if status else None

    def update_video_status(self, filename: str, status: Dict) -> None:
        """Actualiza el estado del video en Redis"""
        self.redis_client.set(
            f"video_status:{filename}",
            json.dumps(status)
        )

    def save_video(self, filename: str, content: bytes) -> Path:
        """Guarda un video en el directorio de videos"""
        video_path = self.videos_dir / filename
        with open(video_path, "wb") as f:
            f.write(content)
        return video_path