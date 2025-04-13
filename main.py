from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.v1.edi.router import router as edi_router
from api.v1.health import router as health_router

app = FastAPI(
    title="Cargo EDI API",
    description="API for generating and decoding cargo EDI messages",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(edi_router)
app.include_router(health_router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Cargo EDI API",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }

if __name__ == "__main__":
    import uvicorn