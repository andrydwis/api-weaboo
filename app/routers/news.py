import base64
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


@router.get("/recent")
@cache(expire=3600)
async def get_recent_news():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "DNT": "1",  # Do Not Track
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    html = httpx.get(
        app_url,
        follow_redirects=True,
        headers=headers,
    )

    soup = BeautifulSoup(html.content, "html.parser")

    news = []

    for news_item in soup.select("div.herald.box"):
        id = base64.b64encode(
            news_item.find("h3").find("a")["href"].replace("/news/", "").encode("utf-8")
        ).decode("utf-8")
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

        print(published_at)

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


@router.get("/{id}", response_model=News)
@cache(expire=3600)
async def get_news(id: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "DNT": "1",  # Do Not Track
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    id = base64.b64decode(id).decode("utf-8")
    html = httpx.get(app_url + "/news/" + id, follow_redirects=True, headers=headers)

    soup = BeautifulSoup(html.content, "html.parser")

    title = soup.find("h1").text.strip().replace("News\n", "")

    description = soup.find("div", class_="meat")

    for img_tag in description.find_all("img"):
        if img_tag.has_attr("data-src"):
            img_tag["src"] = "https://cdn.animenewsnetwork.com" + img_tag["data-src"]
            del img_tag["data-src"]

    description = description.prettify()

    image = (
        "https://cdn.animenewsnetwork.com"
        + soup.find("div", class_="meat").find("img")["src"]
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
