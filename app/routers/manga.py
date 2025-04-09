from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import httpx
from bs4 import BeautifulSoup
from fastapi import APIRouter
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from redis import asyncio as aioredis

from app.models.manga import Chapter, Genre, Manga, MangaChapter, MangaDetail, Pages


@asynccontextmanager
async def lifespan(_: APIRouter) -> AsyncIterator[None]:
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    yield


router = APIRouter(lifespan=lifespan)
app_url = "https://komiku.id"
api_url = "https://api.komiku.id"


@cache()
async def get_cache():
    return 1


@router.get("/search", response_model=list[Manga])
async def search(query: str):
    html = httpx.get(
        api_url + "/?post_type=manga&s=" + query,
        follow_redirects=True,
    )

    soup = BeautifulSoup(html.content, "html.parser")

    mangas = []

    for manga in soup.find_all("div", class_="bge"):
        id = manga.find("a")["href"].split("/")[-2]
        title = manga.find("h3").text.strip()
        description = manga.find("p").text.strip()
        image = manga.find("img")["src"].split("?")[0]
        genre = manga.find("div", class_="tpe1_inf").text.strip().split(" ")[-1]
        genre_id = genre.lower().replace(" ", "-")
        main_genre = Genre(id=genre_id, name=genre)

        mangas.append(
            Manga(
                id=id,
                title=title,
                description=description,
                main_genre=main_genre,
                image=image,
            )
        )

    return mangas


@router.get("/recent", response_model=list[Manga])
@cache(expire=360)
async def get_recent_update(page: int = 1):
    html = httpx.get(
        api_url + "/manga/page/" + str(page) + "/?orderby=modified",
        follow_redirects=True,
    )

    soup = BeautifulSoup(html.content, "html.parser")

    mangas = []

    for manga in soup.find_all("div", class_="bge"):
        id = manga.find("a")["href"].split("/")[-2]
        title = manga.find("h3").text.strip()
        description = manga.find("p").text.strip()
        image = manga.find("img")["src"].split("?")[0]
        genre = manga.find("div", class_="tpe1_inf").text.strip().split(" ")[-1]
        genre_id = genre.lower().replace(" ", "-")
        main_genre = Genre(id=genre_id, name=genre)

        mangas.append(
            Manga(
                id=id,
                title=title,
                description=description,
                main_genre=main_genre,
                image=image,
            )
        )

    return mangas


@router.get("/popular", response_model=list[Manga])
@cache(expire=360)
async def get_popular(page: int = 1):
    html = httpx.get(
        api_url + "/manga/page/" + str(page) + "/?orderby=meta_value_num",
        follow_redirects=True,
    )

    soup = BeautifulSoup(html.content, "html.parser")

    mangas = []

    for manga in soup.find_all("div", class_="bge"):
        id = manga.find("a")["href"].split("/")[-2]
        title = manga.find("h3").text.strip()
        description = manga.find("p").text.strip()
        image = manga.find("img")["src"].split("?")[0]
        genre = manga.find("div", class_="tpe1_inf").text.strip().split(" ")[-1]
        genre_id = genre.lower().replace(" ", "-")
        main_genre = Genre(id=genre_id, name=genre)

        mangas.append(
            Manga(
                id=id,
                title=title,
                description=description,
                main_genre=main_genre,
                image=image,
            )
        )

    return mangas


@router.get("/genres", response_model=list[Genre])
@cache(expire=360)
async def get_genres():
    html = httpx.get(app_url, follow_redirects=True)

    soup = BeautifulSoup(html.text, "html.parser")

    genres = []

    for genre in soup.find("ul", class_="genre").find_all("li"):
        id = genre.find("a")["href"].split("/")[-2]
        name = genre.find("a").text.strip()
        genres.append(
            Genre(
                id=id,
                name=name,
            )
        )

    return genres


@router.get("/genres/{id}", response_model=list[Manga])
@cache(expire=360)
async def get_genre(id: str, page: int = 1):
    html = httpx.get(
        api_url + "/genre/" + id + "/page/" + str(page), follow_redirects=True
    )

    soup = BeautifulSoup(html.text, "html.parser")

    mangas = []

    for manga in soup.find_all("div", class_="bge"):
        id = manga.find("a")["href"].split("/")[-2]
        title = manga.find("h3").text.strip()
        description = manga.find("p").text.strip()
        image = manga.find("img")["src"].split("?")[0]
        genre = manga.find("div", class_="tpe1_inf").text.strip().split(" ")[-1]
        genre_id = genre.lower().replace(" ", "-")
        main_genre = Genre(id=genre_id, name=genre)

        mangas.append(
            Manga(
                id=id,
                title=title,
                description=description,
                main_genre=main_genre,
                image=image,
            )
        )

    return mangas


@router.get("/{id}", response_model=MangaDetail)
@cache(expire=360)
async def get_manga(id: str):
    html = httpx.get(app_url + "/manga/" + id, follow_redirects=True)

    soup = BeautifulSoup(html.content, "html.parser")

    title_tag = soup.find("td", text="Judul Komik")
    title = title_tag.find_next_sibling("td").text.strip()

    description = soup.find("p", class_="desc").text.strip()

    author_tag = soup.find("td", text="Pengarang")
    author = author_tag.find_next_sibling("td").text.strip()

    status_tag = soup.find("td", text="Status")
    status = status_tag.find_next_sibling("td").text.strip()

    image = soup.find("section", id="Informasi").find("img")["src"].split("?")[0]

    genres = []

    genres_section = soup.find("ul", class_="genre")

    for genre in genres_section.find_all("li"):
        genre_id = genre.find("a")["href"].split("/")[-2]
        genre_name = genre.find("a").text.strip()
        genres.append(Genre(id=genre_id, name=genre_name))

    chapters = []

    chapters_section = soup.find("table", id="Daftar_Chapter")

    for chapter in chapters_section.find_all("tr")[1:]:
        chapter_id = chapter.find("a")["href"].split("/")[-2]
        chapter_title = chapter.find("a").text.strip()
        date = chapter.find("td", class_="tanggalseries").text.strip()
        chapters.append(Chapter(id=chapter_id, title=chapter_title, date=date))

    recommendations = []

    recommendation_section = soup.find("section", id="Spoiler")

    for recommendation in recommendation_section.find_all("div", class_="grd"):
        recommendation_id = recommendation.find("a")["href"].split("/")[-2]
        recommendation_title = recommendation.find("div", class_="h4").text.strip()
        recommendation_description = recommendation.find("p").text.strip()
        recommendation_image = recommendation.find("img")["data-src"].split("?")[0]
        genre = (
            recommendation.find("div", class_="tpe1_inf").text.strip().split(" ")[-1]
        )
        genre_id = genre.lower().replace(" ", "-")
        main_genre = Genre(id=genre_id, name=genre)
        recommendations.append(
            Manga(
                id=recommendation_id,
                title=recommendation_title,
                description=recommendation_description,
                main_genre=main_genre,
                image=recommendation_image,
            )
        )

    return MangaDetail(
        id=id,
        title=title,
        description=description,
        author=author,
        status=status,
        image=image,
        genres=genres,
        chapters=chapters,
        recommendations=recommendations,
    )


@router.get("/{id}/chapters/{chapter_id}", response_model=MangaChapter)
@cache(expire=360)
async def get_chapter(id: str, chapter_id: str):
    html = httpx.get(app_url + "/" + chapter_id, follow_redirects=True)

    soup = BeautifulSoup(html.text, "html.parser")

    title_tag = soup.find("td", text="Judul")
    title = title_tag.find_next_sibling("td").text.strip()

    date_tag = soup.find("td", text="Tanggal Rilis")
    date = date_tag.find_next_sibling("td").text.strip()

    pages = []

    for page in soup.find_all("img", class_="ww"):
        page_number = page["id"]
        image = page["src"]
        pages.append(Pages(page_number=page_number, image=image))

    return MangaChapter(id=chapter_id, title=title, date=date, pages=pages)
