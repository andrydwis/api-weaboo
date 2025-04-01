from pydantic import BaseModel


class News(BaseModel):
    id: str
    title: str
    description: str
    category: str
    image: str
    published_at: str
