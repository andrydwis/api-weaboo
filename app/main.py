import os

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Security, status
from fastapi.security import APIKeyHeader

from app.routers import ai, anime, manga, news
from app.routers.tools import social_media_downloader

load_dotenv()
api_key_header = APIKeyHeader(name="API-Key")


def check_api_key(api_key: str = Security(api_key_header)):
    if api_key != os.getenv("APP_API_KEY"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API Key"
        )
    return True


app = FastAPI()
app.include_router(
    ai.router, prefix="/ai", tags=["ai"], dependencies=[Depends(check_api_key)]
)
app.include_router(anime.router, prefix="/anime", tags=["anime"])
app.include_router(manga.router, prefix="/manga", tags=["manga"])
app.include_router(news.router, prefix="/news", tags=["news"])
app.include_router(
    social_media_downloader.router,
    prefix="/tools/social-media-downloader",
    tags=["tools"],
)


@app.get("/")
async def root():
    return {"status": "ok", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)
