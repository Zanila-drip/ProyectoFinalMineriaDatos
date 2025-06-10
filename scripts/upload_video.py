import requests
import sys
from pathlib import Path

def upload_video(video_path: str, camera_id: str = "cam1"):
    """
    Sube un video a la API de la cámara especificada
    
    Args:
        video_path: Ruta al archivo de video
        camera_id: ID de la cámara (default: cam1)
    """
    # Verificar que el archivo existe
    video_file = Path(video_path)
    if not video_file.exists():
        print(f"Error: El archivo {video_path} no existe")
        return
    
    # URL de la API
    api_url = f"http://localhost:8001/api/v1/upload/{camera_id}"
    
    print(f"Subiendo video {video_file.name} a la cámara {camera_id}...")
    
    # Preparar el archivo para subir
    with open(video_file, "rb") as f:
        files = {"video": (video_file.name, f, "video/mp4")}
        response = requests.post(api_url, files=files)
    
    # Verificar la respuesta
    if response.status_code == 200:
        print("¡Video subido exitosamente!")
        print("Respuesta:", response.json())
    else:
        print(f"Error al subir el video: {response.status_code}")
        print("Detalles:", response.text)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python upload_video.py <ruta_al_video> [camera_id]")
        print("Ejemplo: python upload_video.py videos/tradffic5.mp4 cam1")
        sys.exit(1)
    
    video_path = sys.argv[1]
    camera_id = sys.argv[2] if len(sys.argv) > 2 else "cam1"
    
    upload_video(video_path, camera_id)