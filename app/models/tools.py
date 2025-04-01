from typing import Any

from pydantic import BaseModel, Field


class VideoFormat(BaseModel):
    format_id: str | None = Field(
        default=None, description="Unique identifier for the format"
    )
    resolution: str | None = Field(
        default=None, description="Video resolution or 'audio only'"
    )
    url: str | None = Field(default=None, description="Direct URL to the media")
    has_audio: bool | None = Field(
        default=None, description="Whether the format contains audio"
    )
    has_video: bool | None = Field(
        default=None, description="Whether the format contains video"
    )
    bitrate: float | None = Field(
        default=None, description="Audio bitrate in bits per second"
    )
    audio_codec: str | None = Field(default=None, description="Audio codec used")
    ext: str | None = Field(default=None, description="File extension/container format")
    file_size: int | None = Field(default=None, description="File size in bytes")
    cookies: dict[str, Any] | None = Field(
        default=None, description="Cookies required for download"
    )


class Metadata(BaseModel):
    platform: str = Field(..., description="Source platform of the video")
    title: str = Field(..., description="Title of the video")
    duration: float | None = Field(default=None, description="Duration in seconds")
    thumbnail: str | None = Field(
        default=None, description="URL to the video thumbnail"
    )
    formats: list[VideoFormat] = Field(
        ..., description="Available formats for download"
    )
