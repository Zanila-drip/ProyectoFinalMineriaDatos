import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient

# Obtener la URL de MongoDB desde las variables de entorno
MONGODB_URL = os.getenv('MONGODB_URL', 'mongodb://mongodb:27017/')

# Cliente síncrono para operaciones que no requieren async
client = MongoClient(MONGODB_URL)
db = client.traffic_system

# Cliente asíncrono para operaciones que requieren async
async_client = AsyncIOMotorClient(MONGODB_URL)
async_db = async_client.traffic_system

# Colecciones
videos_collection = db.videos
detections_collection = db.detections

# Índices
videos_collection.create_index([("camera_id", 1), ("created_at", -1)])
detections_collection.create_index([("video_id", 1), ("frame_number", 1)]) 