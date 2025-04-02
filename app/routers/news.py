from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone

import httpx
from bs4 import BeautifulSoup
from fastapi import APIRouter
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from redis import asyncio as aioredis

from app.models.news import News


@asynccontextmanager
async def lifespan(_: APIRouter) -> AsyncIterator[None]:
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    yield


router = APIRouter(lifespan=lifespan)
app_url = "https://www.animenewsnetwork.com"


@cache()
async def get_cache():
    return 1


@router.get("/recent-news", response_model=list[News])
@cache(expire=360)
async def get_recent_news():
    html = httpx.get(
        app_url,
        follow_redirects=True,
    )

    soup = BeautifulSoup(html.content, "html.parser")

    news = []

    for news_item in soup.select("div.herald.box"):
        id = news_item.find("h3").find("a")["href"].replace("/news/", "")
        title = news_item.find("h3").text.strip()
        category = news_item.find("div", class_="category").text.strip()
        description = news_item.find("div", class_="snippet").text.strip()
        image = (
            "https://cdn.animenewsnetwork.com"
            + news_item.find("div", class_="thumbnail")["data-src"]
        )
        # parse datetime
        published_at = news_item.find("time")["datetime"]
        dt = datetime.fromisoformat(published_at)
        tz = timezone(timedelta(hours=7))
        dt_tz = dt.astimezone(tz)
        published_at = dt_tz.strftime("%d %B %Y, %H:%M")

        if category == "news":
            news.append(
                News(
                    id=id,
                    title=title,
                    description=description,
                    category=category,
                    image=image,
                    published_at=published_at,
                )
            )

    return news


@router.get("/get-news", response_model=News)
@cache(expire=360)
async def get_news(id: str):
    html = httpx.get(app_url + "/news/" + id, follow_redirects=True)

    soup = BeautifulSoup(html.content, "html.parser")

    title = soup.find("h1").text.strip().replace("News\n", "")
    description = soup.find("div", class_="meat").prettify()
    image = (
        "https://cdn.animenewsnetwork.com"
        + soup.find("div", class_="meat").find("img")["data-src"]
    )

    # parse datetime
    published_at = soup.find("time")["datetime"]
    dt = datetime.fromisoformat(published_at)
    tz = timezone(timedelta(hours=7))
    dt_tz = dt.astimezone(tz)
    published_at = dt_tz.strftime("%d %B %Y, %H:%M")

    return News(
        id=id,
        title=title,
        description=description,
        category="news",
        image=image,
        published_at=published_at,
    )
