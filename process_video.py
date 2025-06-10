from traffic_system import TrafficSystem
import cv2
from pymongo import MongoClient
from datetime import datetime
import os
import gridfs
import numpy as np
import imageio

def procesar_video_y_guardar_en_mongo_gridfs(video_path, traffic_system, frame_interval=30, descripcion=""):
    client = MongoClient("mongodb://localhost:27017/")
    db = client['trafico']
    fs = gridfs.GridFS(db)
    videos_col = db['Videos']
    frames_col = db['VideosFrames']

    # Insertar el video y obtener el video_id automáticamente
    video_doc = {
        "nombre": os.path.basename(video_path),
        "ruta": video_path,
        "fecha_subida": datetime.now(),
        "descripcion": descripcion,
        "total_frames": int(cv2.VideoCapture(video_path).get(cv2.CAP_PROP_FRAME_COUNT))
    }
    video_id = videos_col.insert_one(video_doc).inserted_id

    cap = cv2.VideoCapture(video_path)
    frame_count = 0
    saved_count = 0
    estadisticas_autos = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_interval == 0:
            # Procesar el frame con YOLO
            processed_image, detections = traffic_system.detect_objects_from_array(frame)

            # Calcular métricas usando el método analyze_traffic de TrafficSystem
            metrics = traffic_system.analyze_traffic(detections, saved_count, video_id)

            estadisticas_autos.append(metrics.get('by_class', {}).get('car', 0))

            # Guardar imagen procesada en GridFS
            _, buffer = cv2.imencode('.jpg', processed_image)
            file_id = fs.put(buffer.tobytes(), filename=f'processed_{saved_count:04d}.jpg')

            # Guardar en MongoDB con métricas
            frame_doc = {
                "video_id": video_id,
                "frame_num": saved_count,
                "gridfs_id": file_id,
                "detecciones": detections,
                "metricas": metrics
            }
            frames_col.insert_one(frame_doc)

            saved_count += 1

        frame_count += 1

    cap.release()
    print(f"Video y {saved_count} frames procesados y almacenados en MongoDB (GridFS).")
    return video_id, saved_count, estadisticas_autos

def crear_gif(video_id):
    client = MongoClient("mongodb://localhost:27017/")
    db = client['trafico']
    fs = gridfs.GridFS(db)
    frames_col = db['VideosFrames']
    videos_col = db['Videos']

    # Obtener el nombre del video
    video = videos_col.find_one({"_id": video_id})
    if not video:
        print("No se encontró el video en la base de datos.")
        return

    # Crear el nombre del GIF basado en el nombre del video
    video_name = os.path.splitext(video['nombre'])[0]  # Remover la extensión
    gif_path = f'frames_analizados/{video_name}_detections.gif'

    frames_cursor = frames_col.find({"video_id": video_id}).sort("frame_num", 1)
    frames_list = list(frames_cursor)

    frames = []
    for frame_doc in frames_list:
        img_bytes = fs.get(frame_doc['gridfs_id']).read()
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is not None:
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            frames.append(img_rgb)

    if frames:
        imageio.mimsave(gif_path, frames, fps=10, loop=0)
        print(f"GIF guardado en: {gif_path}")
    else:
        print("No se encontraron frames en GridFS para crear el GIF.")

if __name__ == "__main__":
    # Inicializar el sistema de tráfico
    traffic_system = TrafficSystem()
    traffic_system.load_model('yolov8m.pt')

    # Procesar el video
    video_path = 'videos/tradffic2.mp4'
    frame_interval = 30
    descripcion = "Video de tráfico urbano"

    video_id, frame_count, estadisticas_autos = procesar_video_y_guardar_en_mongo_gridfs(
        video_path, traffic_system, frame_interval, descripcion
    )

    # Crear el GIF
    crear_gif(video_id) 