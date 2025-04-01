from fastapi import FastAPI, HTTPException

from app.routers import ai, anime, manga
from app.routers.tools import social_media_downloader

app = FastAPI()
app.include_router(ai.router, prefix="/ai", tags=["ai"])
app.include_router(anime.router, prefix="/anime", tags=["anime"])
app.include_router(manga.router, prefix="/manga", tags=["manga"])
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
