from pydantic import BaseModel, Field


class Genre(BaseModel):
    id: str = Field(examples=["action"])
    name: str = Field(examples=["Action"])


class Anime(BaseModel):
    id: str = Field(examples=["solo-level-s2-sub-indo"])
    title: str = Field(examples=["Solo Leveling Season 2"])
    episodes: int | None = Field(examples=[12])
    image: str = Field(
        examples=["https://otakudesu.cloud/wp-content/uploads/2025/01/145502.jpg"]
    )


class Pagination(BaseModel):
    total_items: int = Field(examples=[20])
    current_page: int = Field(examples=[1])
    has_next_page: bool = Field(examples=[True])
    has_prev_page: bool = Field(examples=[False])


class AnimePagination(BaseModel):
    animes: list[Anime]
    pagination: Pagination


class Episodes(BaseModel):
    id: str = Field(examples=["sl-s2-episode-13-sub-indo"])
    title: str = Field(examples=["Solo Leveling Season 2 Episode 13"])


class AnimeDetail(BaseModel):
    id: str = Field(examples=["solo-level-s2-sub-indo"])
    title: str = Field(examples=["Solo Leveling Season 2"])
    japanese_title: str = Field(examples=["Solo Leveling Season 2"])
    description: str = Field(examples=["Solo Leveling Season 2"])
    image: str = Field(
        examples=["https://otakudesu.cloud/wp-content/uploads/2025/01/145502.jpg"]
    )
    score: str | None = Field(examples=["8.5"])
    type: str | None = Field(examples=["TV"])
    status: str | None = Field(examples=["Ongoing"])
    total_episodes: int | str | None = Field(examples=[12])
    duration: str | None = Field(examples=["24 menit"])
    release_date: str | None = Field(examples=["2025-01-01"])
    producers: list[str] | None = Field(examples=[["Toei Animation"]])
    studio: str | None = Field(examples=["Toei Animation"])
    genres: list[Genre] | None = Field(examples=[[Genre(id="action", name="Action")]])
    episodes: list[Episodes] | None
    recommendations: list[Anime] | None


class Server(BaseModel):
    id: str = Field(examples=["otakudesu"])
    name: str = Field(examples=["OtakuDesu"])


class Download(BaseModel):
    name: str = Field(examples=["OtakuDesu"])
    url: str = Field(
        examples=["https://otakudesu.cloud/episode/solo-level-s2-sub-indo-episode-1"]
    )


class EpisodesDetail(BaseModel):
    id: str = Field(examples=["solo-level-s2-sub-indo"])
    episode_id: str = Field(examples=["solo-level-s2-sub-indo-episode-1"])
    title: str = Field(examples=["Solo Leveling Season 2 Episode 1"])
    default_stream_url: str = Field(
        examples=["https://otakudesu.cloud/episode/solo-level-s2-sub-indo-episode-1"]
    )
    servers: dict[str, list[Server]] | None = Field(
        example=[{"480p": {"id": "otakudesu", "name": "OtakuDesu"}}]
    )
    downloads: dict[str, list[Download]] | None = Field(
        example=[
            {
                "480p": [
                    {
                        "name": "OtakuDesu",
                        "url": "https://otakudesu.cloud/episode/solo-level-s2-sub-indo-episode-1",
                    }
                ]
            }
        ]
    )


class ServerDetail(BaseModel):
    id: str = Field(examples=["otakudesu"])
    server_id: str = Field(examples=["otakudesu"])
    url: str = Field(
        examples=["https://otakudesu.cloud/episode/solo-level-s2-sub-indo-episode-1"]
    )
