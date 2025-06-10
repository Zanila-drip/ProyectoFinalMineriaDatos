from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import video_routes

app = FastAPI(
    title="Sistema de Control de Tráfico - API",
    description="API para pruebas del sistema de control de tráfico",
    version="1.0.0"
)

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rutas
app.include_router(video_routes.router, prefix="/api/v1/videos", tags=["videos"])

@app.get("/")
async def root():
    return {
        "message": "Bienvenido a la API del Sistema de Control de Tráfico",
        "version": "1.0.0",
        "docs_url": "/docs"
    } 