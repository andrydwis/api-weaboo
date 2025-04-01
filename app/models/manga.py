from pydantic import BaseModel


class Genre(BaseModel):
    id: str
    name: str


class Chapter(BaseModel):
    id: str
    title: str
    date: str


class Pages(BaseModel):
    page_number: int
    image: str


class Manga(BaseModel):
    id: str
    title: str
    description: str
    main_genre: Genre
    image: str


class MangaDetail(BaseModel):
    id: str
    title: str
    description: str
    author: str
    status: str
    image: str
    genres: list[Genre]
    chapters: list[Chapter]


class MangaChapter(BaseModel):
    id: str
    title: str
    date: str
    pages: list[Pages]
