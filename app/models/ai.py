from pydantic import BaseModel, Field


class Message(BaseModel):
    role: str = Field(examples=["user"])
    content: str = Field(examples=["Nama kamu siapa?"])


class ChatResponse(BaseModel):
    role: str = Field(examples=["assistant"])
    content: str | list | dict | None = Field(examples=["Nama aku Midori Chan!"])
    model: str = Field(examples=["gemini-2.0-flash-lite"])
    histories: list[Message]
