from pymongo import MongoClient
import gridfs

def check_mongodb():
    # Conectar a MongoDB
    client = MongoClient("mongodb://localhost:27017/")
    db = client['trafico']
    
    # Verificar colecciones
    print("Colecciones existentes:", db.list_collection_names())
    
    # Verificar documentos en cada colección
    for collection in ['Videos', 'VideosFrames', 'VideosReconstruidos']:
        count = db[collection].count_documents({})
        print(f"Documentos en {collection}: {count}")
    
    # Verificar archivos en GridFS
    fs = gridfs.GridFS(db)
    gridfs_count = fs.files.count_documents({})
    print(f"Archivos en GridFS: {gridfs_count}")

if __name__ == "__main__":
    check_mongodb() 