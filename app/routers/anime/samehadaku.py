import base64
import json
import re
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import httpx
from bs4 import BeautifulSoup
from fastapi import APIRouter, HTTPException
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from redis import asyncio as aioredis

from app.models.anime import Anime, AnimePagination, Genre, Pagination


@asynccontextmanager
async def lifespan(_: APIRouter) -> AsyncIterator[None]:
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    yield


router = APIRouter(lifespan=lifespan)
app_url = "https://samehadaku.mba"


@cache()
async def get_cache():
    return 1


@router.get("/search", response_model=list[Anime])
async def search(query: str):
    pass


@router.get("/ongoing", response_model=AnimePagination)
async def ongoing(page: int = 1):
    html = httpx.get(
        app_url + "/anime-terbaru" + "/page" + "/" + str(page), follow_redirects=True
    )
    soup = BeautifulSoup(html.content, "html.parser")

    animes_section = soup.find("div", class_="post-show").find("ul")

    animes = []

    for anime in animes_section.find_all("li"):
        id = anime.find("a")["href"].split("/")[-2]
        try:
            episodes = int(anime.find("span").find("author").text.strip())
        except (AttributeError, IndexError, ValueError):
            episodes = None
        title = anime.find("h2").text.strip()
        image = anime.find("img")["src"]
        animes.append(
            Anime(
                id=id,
                title=title,
                episodes=episodes,
                image=image,
            )
        )

    pagination = soup.find("div", class_="pagination")
    current_page = pagination.find("span", class_="page-numbers current")
    has_next_page = current_page.find_next_sibling("a") is not None
    has_prev_page = current_page.find_previous_sibling("a") is not None

    return AnimePagination(
        animes=animes,
        pagination=Pagination(
            total_items=len(animes),
            current_page=page,
            has_next_page=has_next_page,
            has_prev_page=has_prev_page,
        ),
    )


@router.get("/genres", response_model=list[Genre])
async def genres():
    html = httpx.get(app_url + "/daftar-anime-2", follow_redirects=True)

    soup = BeautifulSoup(html.text, "html.parser")

    genres_section = soup.find("td", class_="filter_act genres")

    genres = []

    for genre in genres_section.find_all("label", class_="tax_fil"):
        id = genre.find("input")["value"]
        name = genre.text.strip()
        genres.append(
            Genre(
                id=id,
                name=name,
            )
        )

    return genres


@router.get("/genres/{id}", response_model=AnimePagination)
async def genres_anime(id: str, page: int = 1):
    html = httpx.get(
        app_url + "/genre/" + id + "/page/" + str(page),
        follow_redirects=True,
    )

    print(html.url)

    if html.url != (
        app_url + "/genre" + "/" + id + "/page" + "/" + str(page)
    ) and html.url != (app_url + "/genre" + "/" + id + "/"):
        raise HTTPException(status_code=404, detail="Genre not found")

    soup = BeautifulSoup(html.text, "html.parser")

    animes_section = soup.find("div", class_="relat")

    animes = []

    for anime in animes_section.find_all("div", class_="animepost"):
        id = anime.find("a")["href"].split("/")[-2]
        title = anime.find("h2").text.strip()
        image = anime.find("img")["src"]
        animes.append(
            Anime(
                id=id,
                title=title,
                episodes=None,
                image=image,
            )
        )

    pagination = soup.find("div", class_="pagination")
    current_page = pagination.find("span", class_="page-numbers current")
    has_next_page = current_page.find_next_sibling("a") is not None
    has_prev_page = current_page.find_previous_sibling("a") is not None

    return AnimePagination(
        animes=animes,
        pagination=Pagination(
            total_items=len(animes),
            current_page=page,
            has_next_page=has_next_page,
            has_prev_page=has_prev_page,
        ),
    )
