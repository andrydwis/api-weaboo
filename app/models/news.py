from pydantic import BaseModel, Field


class News(BaseModel):
    id: str = Field(examples=["solo-leveling-season-2"])
    title: str = Field(examples=["Solo Leveling Season 2"])
    description: str = Field(examples=["Solo Leveling Season 2 is an anime series..."])
    category: str = Field(examples=["news"])
    image: str = Field(
        examples=["https://otakudesu.cloud/wp-content/uploads/2025/01/145502.jpg"]
    )
    published_at: str = Field(examples=["2021-01-01"])
