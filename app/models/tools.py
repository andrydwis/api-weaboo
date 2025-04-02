from typing import Any

from pydantic import BaseModel, Field


class VideoFormat(BaseModel):
    format_id: str | None = Field(examples=["137"])

    resolution: str | None = Field(examples=["1080p"])

    url: str | None = Field(examples=["https://example.com/video.mp4"])
    has_audio: bool | None = Field(examples=[True])
    has_video: bool | None = Field(examples=[True])
    bitrate: float | None = Field(examples=[1000000.0])
    audio_codec: str | None = Field(examples=["aac"])
    ext: str | None = Field(examples=["mp4"])
    file_size: int | None = Field(examples=[100000000])
    cookies: dict[str, Any] | None = Field(examples=[{"key": "value"}])


class Metadata(BaseModel):
    platform: str = Field(examples=["YouTube"])
    title: str = Field(examples=["Example Video Title"])
    duration: float | None = Field(examples=[120.0])
    thumbnail: str | None = Field(examples=["https://example.com/thumbnail.jpg"])
    formats: list[VideoFormat]
