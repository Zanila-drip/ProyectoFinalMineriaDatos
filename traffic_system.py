import os
import cv2
import numpy as np
from pathlib import Path
from ultralytics import YOLO
import pymongo
from datetime import datetime
import json
from bson import ObjectId
import imageio
import threading
import queue
import time

class CameraProcessor:
    def __init__(self, camera_id, video_path, model_path='yolov8m.pt'):
        self.camera_id = camera_id
        self.video_path = video_path
        self.model = YOLO(model_path)
        self.frame_queue = queue.Queue()
        self.is_running = False
        
    def process_frame(self, frame):
        results = self.model(frame, conf=0.5)
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
        
        return detections
    
    def run(self):
        self.is_running = True
        cap = cv2.VideoCapture(self.video_path)
        
        while self.is_running and cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            detections = self.process_frame(frame)
            self.frame_queue.put({
                'timestamp': datetime.now(),
                'camera_id': self.camera_id,
                'detections': detections
            })
            
        cap.release()

class TrafficCoordinator:
    def __init__(self, mongo_uri="mongodb://localhost:27017/"):
        self.client = pymongo.MongoClient(mongo_uri)
        self.db = self.client['traffic_analysis']
        self.cameras = {}
        self.decision_queue = queue.Queue()
        
    def add_camera(self, camera_id, video_path):
        camera = CameraProcessor(camera_id, video_path)
        self.cameras[camera_id] = camera
        return camera
    
    def start_all_cameras(self):
        for camera in self.cameras.values():
            thread = threading.Thread(target=camera.run)
            thread.start()
    
    def process_detections(self):
        while True:
            # Recopilar datos de todas las cámaras
            camera_data = {}
            for camera_id, camera in self.cameras.items():
                try:
                    data = camera.frame_queue.get_nowait()
                    camera_data[camera_id] = data
                except queue.Empty:
                    continue
            
            if camera_data:
                # Aquí implementaremos la lógica de decisión
                # Por ahora solo guardamos los datos
                self.save_to_mongodb(camera_data)
            
            time.sleep(0.1)  # Evitar sobrecarga de CPU
    
    def save_to_mongodb(self, camera_data):
        collection = self.db['camera_detections']
        collection.insert_one({
            'timestamp': datetime.now(),
            'camera_data': camera_data
        })
    
    def make_decision(self):
        # Aquí implementaremos la lógica de decisión del semáforo
        # basada en los datos de todas las cámaras
        pass

def main():
    # Configuración de cámaras
    cameras_config = {
        'cam1': 'videos/traffic1.mp4',
        'cam2': 'videos/traffic2.mp4',
        'cam3': 'videos/traffic3.mp4',
        'cam4': 'videos/traffic4.mp4'
    }
    
    # Inicializar coordinador
    coordinator = TrafficCoordinator()
    
    # Agregar cámaras
    for camera_id, video_path in cameras_config.items():
        coordinator.add_camera(camera_id, video_path)
    
    # Iniciar procesamiento
    coordinator.start_all_cameras()
    
    # Iniciar procesamiento de detecciones
    coordinator.process_detections()

if __name__ == "__main__":
    main()