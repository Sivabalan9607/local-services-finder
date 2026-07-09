from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.routes import auth, services

app = FastAPI(title="Service Finder Pro API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(services.router)


@app.on_event("startup")
def on_start():
    init_db()
    from app.routes.services import mount_uploads
    mount_uploads(app)


@app.get("/")
def root():
    return {"message": "Service Finder Pro API is running"}
