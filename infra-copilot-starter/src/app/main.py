
from fastapi import FastAPI
from .api import router as api_router

app = FastAPI(title="Infra Copilot", version="0.1.0")
app.include_router(api_router)

@app.get("/")
def root():
    return {"name": "infra-copilot", "status": "up"}
