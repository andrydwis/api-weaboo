import os

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from fastapi_cache import FastAPICache

from app.routers import ai, manga, news
from app.routers.anime import otakudesu, samehadaku
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
app.include_router(
    otakudesu.router, prefix="/otakudesu/anime", tags=["anime otakudesu"]
)
app.include_router(
    samehadaku.router, prefix="/samehadaku/anime", tags=["anime samehadaku"]
)
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


@app.get("/clear")
async def clear():
    return await FastAPICache.clear()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)
