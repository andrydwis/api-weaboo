from pydantic import BaseModel, Field


class Message(BaseModel):
    role: str = Field(examples=["user"])
    content: str = Field(examples=["Siapa karakter ini?"])
    files: list[str] | None = Field(examples=[["files/3amiatb99u3g"]])


class Chat(BaseModel):
    role: str = Field(examples=["model"])
    content: str | list | dict | None = Field(examples=["Nama aku Midori Chan!"])
    model: str = Field(examples=["gemini-2.0-flash-lite"])
    histories: list[Message]
