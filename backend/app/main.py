from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import engine, Base
from app.auth.router import router as auth_router
from app.api.upload import router as upload_router
from app.api.analysis import router as analysis_router
from app.api.history import router as history_router
from app.api.chat import router as chat_router
from app.api.reports import router as reports_router

from app.db.database import engine, Base
from app.db.firebase import init_firebase

# Auto-create all database tables and initialize Firebase Cloud Firestore
Base.metadata.create_all(bind=engine)
init_firebase()

app = FastAPI(
    title="AI Financial Intelligence Platform API",
    description="Enterprise-grade financial intelligence engine for parsing accounting workbooks, statement generation, financial ratios, corporate finance, and AI insights.",
    version="1.0.0"
)

# Proper CORS configuration for local dev and credential passing
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ],
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:[0-9]+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(upload_router)
app.include_router(analysis_router)
app.include_router(history_router)
app.include_router(chat_router)
app.include_router(reports_router)

@app.get("/")
def read_root():
    return {
        "status": "ONLINE",
        "system": "AI Financial Intelligence Platform API",
        "docs": "/docs"
    }

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    from fastapi.responses import Response
    return Response(status_code=204)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
