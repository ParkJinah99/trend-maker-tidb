from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import os

from src.api.auth.routes import auth_router
from src.api.threads.routes import threads_router
from src.api.dashboard.routes import dashboard_router

app = FastAPI()

frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
origins = [
    frontend_url,
    "https://trend-maker-frontend.onrender.com",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(threads_router, prefix="/threads", tags=["threads"])
app.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])


@app.get("/")
async def read_root():
    return {"message": "Welcome to Trend-Maker!"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
