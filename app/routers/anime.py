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
from idna import decode
from redis import asyncio as aioredis


@asynccontextmanager
async def lifespan(_: APIRouter) -> AsyncIterator[None]:
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    yield


router = APIRouter(lifespan=lifespan)
app_url = "https://otakudesu.cloud"


@cache()
async def get_cache():
    return 1


@router.get("/search")
async def search(query: str):
    html = httpx.get(
        app_url + "/?s=" + query + "&post_type=anime",
        follow_redirects=True,
    )

    soup = BeautifulSoup(html.content, "html.parser")

    animes_section = soup.find("ul", class_="chivsrc")

    animes = []

    for anime in animes_section.find_all("li"):
        id = anime.find("a")["href"].split("/")[-2]
        title = re.sub(
            r"\s+",
            " ",
            re.sub(r"\(.*?\)", "", anime.find("h2").text)
            .replace("Subtitle Indonesia", "")
            .strip(),
        )
        image = anime.find("img")["src"]
        animes.append(
            {
                "id": id,
                "title": title,
                "image": image,
            }
        )

    return animes


@router.get("/ongoing-anime")
@cache(expire=360)
async def ongoing_anime(page: int = 1):
    html = httpx.get(
        app_url + "/ongoing-anime" + "/page" + "/" + str(page), follow_redirects=True
    )

    soup = BeautifulSoup(html.text, "html.parser")

    animes_section = soup.find("div", class_="venz")

    animes = []

    for anime in animes_section.find_all("li"):
        id = anime.find("a")["href"].split("/")[-2]
        title = anime.find("h2", class_="jdlflm").text
        episodes = anime.find("div", class_="epz").text.split(" ")[2]
        image = anime.find("img")["src"]
        animes.append(
            {
                "id": id,
                "title": title,
                "episodes": episodes,
                "image": image,
            }
        )

    pagination = soup.find("div", class_="pagination")
    has_next_page = pagination.find("a", class_="next page-numbers") is not None
    has_prev_page = pagination.find("a", class_="prev page-numbers") is not None

    return {
        "animes": animes,
        "pagination": {
            "total_items": len(animes),
            "current_page": page,
            "has_next_page": has_next_page,
            "has_prev_page": has_prev_page,
        },
    }


@router.get("/genres")
@cache(expire=360)
async def get_genres():
    html = httpx.get(
        app_url + "/genre-list",
        follow_redirects=True,
    )

    soup = BeautifulSoup(html.text, "html.parser")

    genres = []
    genres_section = soup.find("ul", class_="genres").find("li")
    for genre in genres_section.find_all("a"):
        id = genre["href"].split("/")[-2]
        title = genre.text
        genres.append(
            {
                "id": id,
                "title": title,
            }
        )

    return genres


@router.get("/genres/{id}")
@cache(expire=360)
async def get_genres_anime(id: str, page: int = 1):
    html = httpx.get(
        app_url + "/genres" + "/" + id + "/page" + "/" + str(page),
        follow_redirects=True,
    )

    if html.url != app_url + "/genres" + "/" + id + "/page" + "/" + str(page):
        raise HTTPException(status_code=404, detail="Genre not found")

    soup = BeautifulSoup(html.text, "html.parser")

    animes = []
    for anime in soup.find_all("div", class_="col-anime"):
        id = (
            anime.find("div", class_="col-anime-title").find("a")["href"].split("/")[-2]
        )
        title = anime.find("div", class_="col-anime-title").find("a").text
        episodes = anime.find("div", class_="col-anime-eps").text.split(" ")[0]
        image = anime.find("img")["src"]
        animes.append(
            {
                "id": id,
                "title": title,
                "episodes": episodes,
                "image": image,
            }
        )

    pagination = soup.find("div", class_="pagination")
    has_next_page = pagination.find("a", class_="next page-numbers") is not None
    has_prev_page = pagination.find("a", class_="prev page-numbers") is not None

    return {
        "animes": animes,
        "pagination": {
            "total_items": len(animes),
            "current_page": page,
            "has_next_page": has_next_page,
            "has_prev_page": has_prev_page,
        },
    }


@router.get("/{id}")
@cache(expire=360)
async def get_anime(id: str):
    html = httpx.get(app_url + "/anime" + "/" + id, follow_redirects=True)

    # if redirected to other page, return error
    if html.url != app_url + "/anime/" + id:
        raise HTTPException(status_code=404, detail="Anime not found")

    soup = BeautifulSoup(html.text, "html.parser")

    info_section = soup.find("div", class_="infozingle")

    title = (
        info_section.find("b", text="Judul")
        .parent.get_text(strip=True)
        .split(":")[1]
        .strip()
    )

    japanese_title = (
        info_section.find("b", text="Japanese")
        .parent.get_text(strip=True)
        .split(":")[1]
        .strip()
    )

    description = soup.find("div", class_="sinopc").get_text(strip=True)

    image = soup.find("div", class_="fotoanime").find("img")["src"]

    score = (
        info_section.find("b", text="Skor")
        .parent.get_text(strip=True)
        .split(":")[1]
        .strip()
    )

    producers = (
        info_section.find("b", text="Produser")
        .parent.get_text(strip=True)
        .split(":")[1]
        .strip()
        .split(", ")
    )

    type = (
        info_section.find("b", text="Tipe")
        .parent.get_text(strip=True)
        .split(":")[1]
        .strip()
    )

    status = (
        info_section.find("b", text="Status")
        .parent.get_text(strip=True)
        .split(":")[1]
        .strip()
    )

    total_episodes = (
        info_section.find("b", text="Total Episode")
        .parent.get_text(strip=True)
        .split(":")[1]
        .strip()
    )

    duration = (
        info_section.find("b", text="Durasi")
        .parent.get_text(strip=True)
        .split(":")[1]
        .strip()
    )

    release_date = (
        info_section.find("b", text="Tanggal Rilis")
        .parent.get_text(strip=True)
        .split(":")[1]
        .strip()
    )

    Studio = (
        info_section.find("b", text="Studio")
        .parent.get_text(strip=True)
        .split(":")[1]
        .strip()
    )

    genres_section = info_section.find("b", text="Genre").parent
    genres = []
    for genre in genres_section.find_all("a"):
        id = genre["href"].split("/")[-2]
        name = genre.get_text(strip=True)
        genres.append({"id": id, "name": name})

    episodes_section = soup.find_all("div", class_="episodelist")
    episodes_section = episodes_section[1]
    print(episodes_section.prettify())
    episodes = []
    for episode in episodes_section.find("ul").find_all("li"):
        print(episode.prettify())
        id = episode.find("a")["href"].split("/")[-2]
        title = (
            re.search(r"\b\d+\b", episode.find("a").get_text(strip=True)) or [None]
        )[0] or episode.find("a").get_text(strip=True)
        episodes.append({"id": id, "title": title})

    recommendations_section = soup.find("div", id="recommend-anime-series")
    recommendations = []
    for recommendation in recommendations_section.find_all("div", class_="isi-konten"):
        id = recommendation.find("a")["href"].split("/")[-2]
        title = recommendation.find("span", class_="judul-anime").get_text(strip=True)
        image = recommendation.find("img")["src"]
        recommendations.append({"id": id, "title": title, "image": image})

    return {
        "id": id,
        "title": title,
        "japanese_title": japanese_title,
        "description": description,
        "image": image,
        "score": score,
        "type": type,
        "status": status,
        "total_episodes": total_episodes,
        "duration": duration,
        "release_date": release_date,
        "producers": producers,
        "Studio": Studio,
        "genres": genres,
        "episodes": episodes,
        "recommendations": recommendations,
    }


@router.get("/{id}/episodes/{episode_id}")
@cache(expire=360)
async def get_episode(id: str, episode_id: str):
    html = httpx.get(
        app_url + "/episode/" + episode_id,
        follow_redirects=True,
    )

    soup = BeautifulSoup(html.content, "html.parser")

    if html.url != app_url + "/episode" + "/" + episode_id:
        raise HTTPException(status_code=404, detail="Episode not found")

    title = soup.find("h1", class_="posttl").get_text(strip=True)

    default_stream_url = soup.find("div", class_="responsive-embed-stream").find(
        "iframe"
    )["src"]

    servers_section = soup.find("div", class_="mirrorstream")
    qualtiy_servers = {}
    qualities = servers_section.find_all("ul")
    for quality in qualities:
        quality_name = quality.get("class")[0].replace("m", "")
        servers = []
        for server in quality.find_all("li"):
            server_id = server.find("a")["data-content"]
            server_name = server.get_text(strip=True).lower()

            servers.append(
                {
                    "id": server_id,
                    "name": server_name,
                }
            )
        qualtiy_servers[quality_name] = servers

    downloads_section = soup.find("div", class_="download")
    download_servers = {}
    for download in downloads_section.find_all("li"):
        quality_name = download.find("strong").get_text(strip=True).split(" ")[1]
        servers = []
        for server in download.find_all("a"):
            server_name = server.get_text(strip=True).lower()
            server_url = server["href"]

            servers.append(
                {
                    "name": server_name,
                    "url": server_url,
                }
            )
        download_servers[quality_name] = servers

    return {
        "id": id,
        "episode_id": episode_id,
        "title": title,
        "default_stream_url": default_stream_url,
        "servers": qualtiy_servers,
        "downloads": download_servers,
    }


@router.get("/{id}/servers/{server_id}")
@cache(expire=360)
async def get_server(id: str, server_id: str):
    nonce = getNonce()

    decode_server = json.loads(base64.b64decode(server_id).decode("utf-8"))

    get_server = httpx.post(
        url=app_url + "/wp-admin/admin-ajax.php",
        data={
            "action": "2a3505c93b0035d3f455df82bf976b84",
            "nonce": nonce["data"],
            "id": decode_server["id"],
            "i": decode_server["i"],
            "q": decode_server["q"],
        },
    ).json()

    html = base64.b64decode(get_server["data"]).decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")

    return {
        "id": id,
        "server_id": server_id,
        "url": soup.find("iframe")["src"],
    }


def getNonce():
    json = httpx.post(
        url=app_url + "/wp-admin/admin-ajax.php",
        data={
            "action": "aa1208d27f29ca340c92c66d1926f13f",
        },
    ).json()

    return json
