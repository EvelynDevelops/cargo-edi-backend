from fastapi import FastAPI
from api.generate_edi_route import router as edi_router
from api.decode_edi_route import router as decode_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(edi_router)
app.include_router(decode_router)

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI"}