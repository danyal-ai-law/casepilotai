from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import auth

app = FastAPI(
    title="CasePilot AI",
    version="1.0.0"
)

# CORS (frontend connection)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(auth.router)

@app.get("/")
def home():
    return {"message": "CasePilot AI is running"}

@app.get("/health")
def health():
    return {"status": "ok"}
