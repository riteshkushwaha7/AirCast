import firebase_admin
from firebase_admin import credentials
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import setup_logging

settings = get_settings()


def create_application() -> FastAPI:
    setup_logging()

    if not firebase_admin._apps:
        if settings.firebase_project_id and settings.firebase_private_key and settings.firebase_client_email:
            # Building a full service account dictionary to satisfy google-auth requirements
            service_account_info = {
                "type": "service_account",
                "project_id": settings.firebase_project_id,
                "private_key": settings.firebase_private_key.replace("\\n", "\n"),
                "client_email": settings.firebase_client_email,
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{settings.firebase_client_email.replace('@', '%40')}"
            }
            firebase_admin.initialize_app(credentials.Certificate(service_account_info))
        else:
            # Production default: Initialize using GOOGLE_APPLICATION_CREDENTIALS environment variable
            firebase_admin.initialize_app()

    app = FastAPI(
        title=settings.project_name,
        debug=settings.debug,
        version="0.2.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins.split(","),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

    register_exception_handlers(app)

    app.include_router(api_router, prefix=settings.api_v1_prefix)

    @app.get("/")
    def root() -> dict:
        return {"service": settings.project_name, "status": "ok"}

    return app


app = create_application()
