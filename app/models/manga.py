from pydantic import BaseModel, Field


class Genre(BaseModel):
    id: str = Field(examples=["action"])
    name: str = Field(examples=["Action"])


class Chapter(BaseModel):
    id: str = Field(examples=["solo-leveling-chapter-1"])
    title: str = Field(examples=["Solo Leveling Chapter 1"])
    date: str = Field(examples=["2024-01-01"])


class Pages(BaseModel):
    page_number: int = Field(examples=[1])
    image: str = Field(
        examples=["https://otakudesu.cloud/wp-content/uploads/2025/01/145502.jpg"]
    )


class Manga(BaseModel):
    id: str = Field(examples=["solo-leveling"])
    title: str = Field(examples=["Solo Leveling"])
    description: str = Field(examples=["Solo Leveling is a manga series..."])
    main_genre: Genre
    image: str = Field(
        examples=["https://otakudesu.cloud/wp-content/uploads/2025/01/145502.jpg"]
    )


class MangaDetail(BaseModel):
    id: str = Field(examples=["solo-leveling"])
    title: str = Field(examples=["Solo Leveling"])
    description: str = Field(examples=["Solo Leveling is a manga series..."])
    author: str = Field(examples=["Chugong"])
    status: str = Field(examples=["Ongoing"])
    image: str = Field(
        examples=["https://otakudesu.cloud/wp-content/uploads/2025/01/145502.jpg"]
    )
    genres: list[Genre]
    chapters: list[Chapter]


class MangaChapter(BaseModel):
    id: str = Field(examples=["solo-leveling-chapter-1"])
    title: str = Field(examples=["Solo Leveling Chapter 1"])
    date: str = Field(examples=["2021-01-01"])
    pages: list[Pages]
