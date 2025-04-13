from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.v1.edi.router import router as edi_router

app = FastAPI(
    title="Cargo EDI API",
    description="API for generating and decoding EDI messages",
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

if __name__ == "__main__":
    import uvicorn
@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI"}