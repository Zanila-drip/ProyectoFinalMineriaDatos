import os
from datetime import datetime
from pathlib import Path
import shutil
from typing import List, Optional
import redis
import json

class VideoService:
    def __init__(self):
        self.videos_dir = Path("videos")
        self.videos_dir.mkdir(exist_ok=True)
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)

    async def save_video(self, file, camera_id: str) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"traffic_{camera_id}_{timestamp}.mp4"
        file_path = self.videos_dir / filename

        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Publicar evento de nuevo video
        self.redis_client.publish(
            'new_videos',
            json.dumps({
                'filename': filename,
                'camera_id': camera_id,
                'timestamp': timestamp
            })
        )

        return filename

    def get_videos(self) -> List[dict]:
        videos = []
        for video in self.videos_dir.glob("*.mp4"):
            videos.append({
                "filename": video.name,
                "size": video.stat().st_size,
                "created_at": datetime.fromtimestamp(video.stat().st_ctime)
            })
        return videos

    def get_video_path(self, filename: str) -> Optional[Path]:
        video_path = self.videos_dir / filename
        return video_path if video_path.exists() else None

    def update_video_status(self, filename: str, status: str, results: Optional[dict] = None):
        key = f"video:{filename}"
        data = {
            'status': status,
            'updated_at': datetime.now().isoformat()
        }
        if results:
            data['results'] = results
        self.redis_client.hmset(key, data)

    def get_video_status(self, filename: str) -> Optional[dict]:
        key = f"video:{filename}"
        data = self.redis_client.hgetall(key)
        return data if data else None 