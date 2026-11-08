import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes.webhook import router as webhook_router
from app.routes.api import router as api_router
from app.routes.pages import router as pages_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

app = FastAPI(
    title="阪口源太（福井県高浜町）公式LINE連携 Webアプリケーション・AI Bot基盤",
    version="1.0.0",
    description="2027年春の高浜町議会議員選挙に向けたLINE連携AI対話BotおよびLIFFプラットフォーム"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static Files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include Routers
app.include_router(webhook_router, prefix="/line", tags=["LINE Messaging API"])
app.include_router(api_router, prefix="/api", tags=["API"])
app.include_router(pages_router, tags=["LIFF / Web Views"])

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "app": "takahama-line-agent",
        "version": "1.0.0",
        "gemini_model": settings.GEMINI_MODEL
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)

