from pymongo import MongoClient
import gridfs

def init_mongodb():
    # Conectar a MongoDB
    client = MongoClient("mongodb://localhost:27017/")
    db = client['trafico']
    
    # Crear GridFS
    fs = gridfs.GridFS(db)
    
    # Crear colecciones si no existen
    collections = ['Videos', 'VideosFrames', 'VideosReconstruidos']
    for collection in collections:
        if collection not in db.list_collection_names():
            db.create_collection(collection)
            print(f"Colección {collection} creada")
    
    # Crear índices
    db.Videos.create_index("nombre")
    db.VideosFrames.create_index([("video_id", 1), ("frame_num", 1)])
    db.VideosReconstruidos.create_index("video_id")
    
    print("MongoDB inicializado correctamente")

if __name__ == "__main__":
    init_mongodb() 