import base64
import json
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from re import A

import httpx
from annotated_types import T
from bs4 import BeautifulSoup
from fastapi import APIRouter, HTTPException
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from redis import asyncio as aioredis

from app.models.anime import (
    Anime,
    AnimeDetail,
    AnimePagination,
    Download,
    Episodes,
    EpisodesDetail,
    Genre,
    Pagination,
    Schedule,
    Server,
    ServerDetail,
)


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
@cache(expire=3600)
async def search(query: str):
    html = httpx.get(
        app_url + "/page/1/?s=" + query,
        follow_redirects=True,
        timeout=30,
    )

    soup = BeautifulSoup(html.content, "html.parser")

    animes = []

    animes_section = soup.find("main", class_="site-main relat")

    for anime in animes_section.find_all("div", class_="animepost"):
        id = anime.find("a")["href"].split("/")[-2]
        title = anime.find("h2").text.strip()
        try:
            image = anime.find("img")["src"]
        except:
            image = "https://placehold.co/400"
        animes.append(
            Anime(
                id=id,
                title=title,
                episodes=None,
                image=image,
            )
        )

    return animes


@router.get("/ongoing", response_model=AnimePagination)
@cache(expire=3600)
async def ongoing(page: int = 1):
    html = httpx.get(
        app_url + "/anime-terbaru" + "/page" + "/" + str(page),
        follow_redirects=True,
        timeout=30,
    )

    soup = BeautifulSoup(html.content, "html.parser")

    animes = []

    animes_section = soup.find("div", class_="post-show").find("ul")

    for anime in animes_section.find_all("li"):
        id = anime.find("a")["href"].split("/")[-2]
        try:
            episodes = int(anime.find("span").find("author").text.strip())
        except (AttributeError, IndexError, ValueError):
            episodes = None
        title = anime.find("h2").text.strip()
        try:
            # image = anime.find("img")["src"]
            anime_detail = await get_anime(id)
            image = anime_detail["image"]
        except:
            image = "https://placehold.co/400"
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


@router.get("/schedule", response_model=list[Schedule])
@cache(expire=3600)
async def schedule():
    days = [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ]

    schedule = []

    for day in days:
        animes_json = httpx.get(
            f"https://samehadaku.mba/wp-json/custom/v1/all-schedule?perpage=20&day={day}&type=schtml",
            follow_redirects=True,
            timeout=30,
        ).json()

        animes = []

        for anime_json in animes_json:

            animes.append(
                Anime(
                    id=anime_json["slug"],
                    title=anime_json["title"],
                    episodes=None,
                    image=anime_json["featured_img_src"] or "https://placehold.co/400",
                )
            )

        schedule.append(
            Schedule(
                day=day,
                animes=animes,
            )
        )

    return schedule


@router.get("/genres", response_model=list[Genre])
@cache(expire=3600)
async def genres():
    html = httpx.get(
        app_url + "/daftar-anime-2",
        follow_redirects=True,
        timeout=30,
    )

    soup = BeautifulSoup(html.text, "html.parser")

    genres = []

    genres_section = soup.find("td", class_="filter_act genres")

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
@cache(expire=3600)
async def genres_anime(id: str, page: int = 1):
    html = httpx.get(
        app_url + "/genre/" + id + "/page/" + str(page),
        follow_redirects=True,
        timeout=30,
    )

    if html.url != (
        app_url + "/genre" + "/" + id + "/page" + "/" + str(page) + "/"
    ) and html.url != (app_url + "/genre" + "/" + id + "/"):
        raise HTTPException(status_code=404, detail="Genre not found")

    soup = BeautifulSoup(html.text, "html.parser")

    animes = []

    animes_section = soup.find("div", class_="relat")

    for anime in animes_section.find_all("div", class_="animepost"):
        id = anime.find("a")["href"].split("/")[-2]
        title = anime.find("h2").text.strip()
        try:
            image = anime.find("img")["src"]
        except:
            image = "https://placehold.co/400"
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


@router.get("/{id}", response_model=AnimeDetail)
@cache(expire=3600)
async def get_anime(id: str):
    html = httpx.get(
        app_url + "/anime" + "/" + id,
        follow_redirects=True,
        timeout=30,
    )

    if html.url != app_url + "/anime/" + id + "/":
        raise HTTPException(status_code=404, detail="Anime not found")

    soup = BeautifulSoup(html.text, "html.parser")

    title = (
        soup.find("h3", class_="anim-detail")
        .text.strip()
        .replace("Detail Anime ", "")
        .strip()
    )

    info_section = soup.find("div", class_="spe")

    japanese_title = (
        soup.find("b", text="Japanese")
        .parent.text.strip()
        .replace("Japanese", "")
        .strip()
    )

    description = (
        soup.find("div", class_="infox").find("div", class_="desc").text.strip()
    )

    try:
        image = soup.find("div", class_="thumb").find("img")["src"]
    except:
        image = "https://placehold.co/400"

    try:
        score = soup.find("span", attrs={"itemprop": "ratingValue"}).text.strip()
    except:
        score = "0"

    producers = (
        info_section.find("b", text="Producers")
        .parent.text.strip()
        .replace("Producers", "")
        .strip()
        .split(", ")
    )

    type = (
        info_section.find("b", text="Type")
        .parent.text.strip()
        .replace("Type", "")
        .strip()
    )

    status = (
        info_section.find("b", text="Status")
        .parent.text.strip()
        .replace("Status", "")
        .strip()
    )

    total_episodes = (
        info_section.find("b", text="Total Episode")
        .parent.text.strip()
        .replace("Total Episode", "")
        .strip()
        or "1"
    )

    duration = (
        info_section.find("b", text="Duration")
        .parent.text.strip()
        .replace("Duration", "")
        .strip()
        or "0 m"
    )

    release_date = (
        info_section.find("b", text="Released:")
        .parent.text.strip()
        .replace("Released:", "")
        .strip()
    )

    season = (
        info_section.find("b", text="Season")
        .parent.text.strip()
        .replace("Season", "")
        .strip()
    )

    studio = (
        info_section.find("b", text="Studio")
        .parent.text.strip()
        .replace("Studio", "")
        .strip()
    )

    genres = []

    genres_section = soup.find("div", class_="genre-info")

    for genre in genres_section.find_all("a"):
        genre_id = genre["href"].split("/")[-1]
        genre_name = genre.text.strip()
        genres.append(Genre(id=genre_id, name=genre_name))

    episodes = []

    episodes_section = soup.find("div", class_="lstepsiode listeps").find("ul")

    for episode in episodes_section.find_all("li"):
        episode_id = episode.find("a")["href"].split("/")[-2]
        episode_title = episode.find("div", class_="epsright").text.strip()
        episodes.append(Episodes(id=episode_id, title=episode_title))

    recommendations = []

    recommendations_section = soup.find("div", class_="rand-animesu").find("ul")

    for recommendation in recommendations_section.find_all("li"):
        recommendation_id = recommendation.find("a")["href"].split("/")[-2]
        recommendation_title = recommendation.find("span", class_="judul").text.strip()
        recommendation_episodes = (
            recommendation.find("span", class_="episode")
            .text.strip()
            .replace("Eps", "")
            .strip()
        )
        try:
            recommendation_image = recommendation.find("img")["src"]
        except:
            recommendation_image = "https://placehold.co/400"
        recommendations.append(
            Anime(
                id=recommendation_id,
                title=recommendation_title,
                episodes=None,
                image=recommendation_image,
            )
        )

    return AnimeDetail(
        id=id,
        title=title,
        japanese_title=japanese_title,
        description=description,
        image=image,
        score=score,
        type=type,
        status=status,
        total_episodes=total_episodes,
        duration=duration,
        release_date=release_date,
        season=season,
        producers=producers,
        studio=studio,
        genres=genres,
        episodes=episodes,
        recommendations=recommendations,
    )


@router.get("/{id}/episodes/{episode_id}", response_model=EpisodesDetail)
@cache(expire=3600)
async def get_episode(id: str, episode_id: str):
    html = httpx.get(
        app_url + "/" + episode_id,
        follow_redirects=True,
        timeout=30,
    )

    if html.url != app_url + "/" + episode_id + "/":
        raise HTTPException(status_code=404, detail="Episode not found")

    soup = BeautifulSoup(html.content, "html.parser")

    title = soup.find("h1", class_="entry-title").text.strip()

    # Initialize the result dictionary
    quality = {}

    # Iterate through each server option
    for server in soup.find_all("div", class_="east_player_option"):
        server_post_id = server.get("data-post")
        server_nume = server.get("data-nume")
        server_type = server.get("data-type")

        server_id = base64.b64encode(
            json.dumps(
                {
                    "post": server_post_id,
                    "nume": server_nume,
                    "type": server_type,
                }
            ).encode("utf-8")
        ).decode("utf-8")

        # Extract the text inside the <span> tag
        server_text = server.find("span").text.strip()

        # Split the text into server name and quality
        parts = server_text.split()
        server_name = " ".join(parts[:-1])  # Everything except the last part
        quality_value = parts[-1]  # The last part is the quality

        # Check if the server is disabled
        is_disabled = "pointer-events: none" in server.get(
            "style", ""
        ) or "text-decoration: line-through" in server.find("span").get("style", "")

        # Skip disabled options
        if is_disabled:
            continue

        # Initialize the quality key as a list if it doesn't exist
        if quality_value not in quality:
            quality[quality_value] = []

        # Append the Server object to the list
        quality[quality_value].append(
            Server(
                id=server_id,
                name=server_name,
            )
        )

    first_quality = next(iter(quality), None)
    if first_quality:
        first_server = quality[first_quality][0]
    default_stream_url = get_server_url(first_server.id)

    download_servers = {}

    format_section = soup.find_all("div", class_="download-eps")

    for format in format_section:
        for download in format.find_all("li"):
            quality_name = download.find("strong").text.strip()
            servers = []
            for server in download.find_all("a"):
                server_name = server.text.strip().lower()
                server_url = server["href"]

                servers.append(
                    Download(
                        name=server_name,
                        url=server_url,
                    )
                )
            download_servers[quality_name] = servers

    return EpisodesDetail(
        id=id,
        episode_id=episode_id,
        title=title,
        default_stream_url=default_stream_url,
        servers=quality,
        downloads=download_servers,
    )


@router.get("/{id}/servers/{server_id}", response_model=ServerDetail)
@cache(expire=3600)
async def get_server(id: str, server_id: str):
    server_url = get_server_url(server_id)

    return ServerDetail(
        id=id,
        server_id=server_id,
        url=server_url,
    )


def get_server_url(server_id: str) -> str:
    # decode server_id
    decode_server = json.loads(base64.b64decode(server_id).decode("utf-8"))
    server_post_id = decode_server["post"]
    server_nume = decode_server["nume"]
    server_type = decode_server["type"]

    get_server = httpx.post(
        url=app_url + "/wp-admin/admin-ajax.php",
        data={
            "action": "player_ajax",
            "post": server_post_id,
            "nume": server_nume,
            "type": server_type,
        },
    )

    soup = BeautifulSoup(get_server.text, "html.parser")

    return soup.find("iframe")["src"]
