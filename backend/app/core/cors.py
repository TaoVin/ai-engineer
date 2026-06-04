from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def setup_cros_middleware(app:FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://localhost:4000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )