from datetime import datetime, timedelta
from typing import Any

import httpx
import yt_dlp
from fastapi import APIRouter, HTTPException

from app.models.tools import Metadata, VideoFormat

router = APIRouter()

# Global cookie file path
COOKIE_FILE = "cookies.txt"


# Define the cookie file path globally or pass it as a parameter
COOKIE_FILE = "cookies.txt"


async def get_cookies(
    platform: str, url: str | None = None, cookie_file: str = "cookies.txt"
) -> bool:
    """
    Fetch cookies from the given URL and save them in Netscape HTTP Cookie File format.

    Args:
        platform (str): The platform name (e.g., "tiktok", "youtube").
        url (Optional[str]): The URL to fetch cookies from. Defaults to None.
        cookie_file (str): The file path to save cookies. Defaults to "cookies.txt".

    Returns:
        bool: True if cookies were successfully saved, False otherwise.
    """
    if not url:
        raise ValueError("URL must be provided.")

    # Validate platform
    if platform not in {"tiktok", "youtube"}:
        raise ValueError(
            "Invalid platform. Supported platforms are 'tiktok' and 'youtube'."
        )

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                        "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                    )
                },
            )
            cookies = response.cookies

            # Write cookies to the file in Netscape HTTP Cookie File format
            with open(cookie_file, "w") as f:
                f.write("# Netscape HTTP Cookie File\n")
                for name, value in cookies.items():
                    domain = ".tiktok.com" if platform == "tiktok" else ".youtube.com"
                    expiration = int((datetime.now() + timedelta(days=365)).timestamp())
                    f.write(
                        f"{domain}\tTRUE\t/\tFALSE\t{expiration}\t{name}\t{value}\n"
                    )

            return True

    except httpx.RequestError as e:
        print(f"HTTP request failed for URL '{url}': {e}")
        return False

    except Exception as e:
        print(f"An unexpected error occurred while fetching cookies: {e}")


def format_cookies(cookies_str: str | None) -> dict[str, str] | None:
    """Format cookies from string to dictionary"""
    if not cookies_str:
        return None

    cookies = {}
    parts = cookies_str.split("; ")
    current_name = None

    for part in parts:
        if "=" in part:
            name, value = part.split("=", 1)
            if not name.lower() in ["domain", "path", "secure", "expires"]:
                current_name = name
                cookies[current_name] = value
        elif part.lower() == "secure":
            if current_name:
                cookies[current_name + "_secure"] = True

    return cookies


@router.get("/download/", response_model=Metadata)
async def download(
    platform: str,
    video_url: str,
):
    """
    Extract metadata (e.g., title, duration, formats, streaming URLs) for a video
    from YouTube, Facebook, TikTok, or other supported platforms.

    Includes:
    - MP4 formats (video with or without audio)
    - Audio-only formats (e.g., .m4a files) with detailed audio information (bitrate, codec, format, etc.)
    """
    # Handle cookies
    if platform == "tiktok" or platform == "youtube":
        if not await get_cookies(platform, video_url):
            raise HTTPException(500, detail="Cookie generation failed")

    # Define yt-dlp options
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "forceurl": True,  # Only fetch the URL, don't download
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        },
    }

    if any(
        domain in video_url.lower()
        for domain in ["tiktok.com", "youtube.com", "youtu.be"]
    ):
        print("TikTok or YouTube URL detected")
        ydl_opts.update(
            {
                "no_watermark": True,
                "cookiefile": COOKIE_FILE,
            }
        )

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            # Extract info without downloading
            info = ydl.extract_info(video_url, download=False)

            # Detect platform automatically
            platform = info.get("extractor_key", "Unknown Platform").capitalize()

            # Filter formats to include MP4 video (with or without audio) and audio-only formats
            filtered_formats = [
                VideoFormat(
                    format_id=fmt.get("format_id"),
                    resolution=(
                        fmt.get("resolution", "audio only")
                        if fmt.get("vcodec") != "none"
                        else "audio only"
                    ),
                    url=fmt.get("url"),
                    has_audio=fmt.get("acodec") != "none",
                    has_video=fmt.get("vcodec") != "none",
                    bitrate=fmt.get("abr"),
                    audio_codec=fmt.get("acodec"),
                    ext=fmt.get("ext"),
                    file_size=fmt.get("filesize") or fmt.get("filesize_approx"),
                    cookies=format_cookies(fmt.get("cookies")),
                )
                for fmt in info.get("formats", [])
                if (
                    (
                        fmt.get("ext") == "mp4" and fmt.get("vcodec") != "none"
                    )  # MP4 video
                    or (
                        fmt.get("acodec") != "none" and fmt.get("vcodec") == "none"
                    )  # Audio
                )
                and not fmt.get("url", "").endswith(".m3u8")  # Exclude .m3u8 playlists
            ]

            return Metadata(
                platform=platform,
                title=info.get("title", "Unknown Title"),
                duration=info.get("duration"),
                thumbnail=info.get("thumbnail"),
                formats=filtered_formats,
            )

        except Exception as e:
            raise HTTPException(
                status_code=400, detail=f"Error processing video: {str(e)}"
            )
