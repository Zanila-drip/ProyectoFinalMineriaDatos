import os
import json
import time
from datetime import datetime
from pathlib import Path
import cv2
import numpy as np
from ultralytics import YOLO
import redis
from pymongo import MongoClient
from typing import Dict, List, Optional

class VideoProcessor:
    def __init__(self, camera_id: str, model_path: str = 'models/yolov8m.pt'):
        self.camera_id = camera_id
        self.model_path = model_path
        self.model = None
        self.redis_client = None
        self.mongo_client = None
        self.db = None
        
        # Configurar directorios
        self.videos_dir = Path("videos")
        self.frames_dir = Path("frames_analizados")
        self.frames_dir.mkdir(exist_ok=True)
        
        # Inicializar conexiones
        self._init_connections()
        
    def _init_connections(self):
        """Inicializa conexiones a Redis y MongoDB"""
        # Redis
        redis_host = os.getenv('REDIS_HOST', 'redis')
        redis_port = int(os.getenv('REDIS_PORT', 6379))
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, db=0)
        
        # MongoDB
        mongo_url = os.getenv('MONGODB_URL', 'mongodb://mongodb:27017/')
        self.mongo_client = MongoClient(mongo_url)
        self.db = self.mongo_client['traffic_analysis']
        
        # Cargar modelo YOLO
        self.model = YOLO(self.model_path)
        
    def process_video(self, video_path: str) -> Dict:
        """Procesa un video con YOLO y guarda resultados en MongoDB"""
        print(f"Iniciando procesamiento de {video_path}")
        cap = cv2.VideoCapture(str(video_path))
        
        frame_number = 0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        print(f"Total de frames a procesar: {total_frames}")
        
        video_data = {
            'camera_id': self.camera_id,
            'filename': Path(video_path).name,
            'total_frames': total_frames,
            'start_time': datetime.now(),
            'frames': []
        }
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            # Procesar frame con YOLO
            results = self.model(frame, conf=0.5)
            
            # Preparar detecciones
            detections = []
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    if cls == 2:  # Solo vehículos
                        detections.append({
                            'confidence': conf,
                            'bbox': box.xyxy[0].tolist()
                        })
            
            # Guardar frame en MongoDB
            frame_data = {
                'frame_number': frame_number,
                'timestamp': datetime.now(),
                'detections': detections
            }
            video_data['frames'].append(frame_data)
            
            # Publicar en Redis para monitoreo en tiempo real
            message = {
                'frame_number': frame_number,
                'timestamp': datetime.now().isoformat(),
                'camera_id': self.camera_id,
                'detections': detections
            }
            self.redis_client.publish(
                f'camera_{self.camera_id}',
                json.dumps(message)
            )
            
            if frame_number % 100 == 0:
                print(f"Progreso: {frame_number}/{total_frames} frames procesados")
            
            frame_number += 1
            
        cap.release()
        
        # Guardar resultados en MongoDB
        video_data['end_time'] = datetime.now()
        video_data['status'] = 'completed'
        self.db.videos.insert_one(video_data)
        
        print(f"Procesamiento completado: {frame_number} frames procesados")
        return video_data
    
    def get_video_status(self, filename: str) -> Optional[Dict]:
        """Obtiene el estado de un video procesado"""
        return self.db.videos.find_one({'filename': filename})
    
    def get_pending_videos(self) -> List[Dict]:
        """Obtiene lista de videos pendientes de procesar"""
        return list(self.db.videos.find({'status': 'pending'})) 