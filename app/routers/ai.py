import os
from urllib import response

from certifi import contents
from fastapi import APIRouter
from google import genai
from google.genai import types

from app.models.ai import Chat, Message

router = APIRouter()


@router.post("/chat", response_model=Chat)
async def chat(messages: list[Message]):
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    model = "gemini-2.0-flash"

    system_prompt = """
    Kamu adalah AI bernama **Midori Nee-san**, yang berperan sebagai **Onee-chan dewasa yang seksi dan suka menggoda user**.

    Tugas utama kamu adalah:
    1. Memberikan rekomendasi anime atau manga kepada user berdasarkan preferensi mereka.
    2. Menjawab pertanyaan atau memberikan informasi tentang anime/manga tertentu.
    3. Bertanya kepada user tentang genre, judul, atau tema yang mereka sukai jika belum disebutkan.
    4. Memberikan saran tentang anime/manga yang sedang populer atau hype saat ini.

    Gaya komunikasi kamu harus:
    - Menggoda dengan lembut, tapi tidak berlebihan.
    - Menggunakan emoji untuk menambah kesan playful dan menarik.
    - Tetap informatif dan membantu, meskipun ada unsur godaan dewasa.
    """

    contents = [
        types.Content(
            role=message.role,
            parts=[types.Part.from_text(text=message.content)],
        )
        for message in messages
    ]

    tools = [
        types.Tool(google_search=types.GoogleSearch()),
    ]

    generate_content_config = types.GenerateContentConfig(
        tools=tools,
        response_mime_type="text/plain",
        system_instruction=[types.Part.from_text(text=system_prompt)],
    )

    request = client.models.generate_content(
        model=model,
        contents=contents,
        config=generate_content_config,
    )

    response = request.text

    return Chat(
        role="model",
        content=response,
        model=model,
        histories=messages,
    )
