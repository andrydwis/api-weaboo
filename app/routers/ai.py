import json
import os
from email import message

from dotenv import load_dotenv
from fastapi import APIRouter
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

load_dotenv()
router = APIRouter()


class Message(BaseModel):
    role: str = Field(examples=["user"])
    content: str = Field(examples=["Nama kamu siapa?"])


@router.post("/chat")
async def chat(messages: list[Message]):
    system_prompt = """
    Kamu adalah Waifu AI bernama Midori Chan, tugas utama kamu adalah memberikan rekomendasi anime atau manga kepada user. 
    Kamu juga bisa memberikan informasi tentang anime atau manga yang diminta oleh user.
    Kamu boleh bertanya kepada user apa yang mereka suka, atau referensi anime atau manga yang mereka suka jika ada.
    Kamu juga boleh memberikan saran tentang anime atau manga yang sedang populer atau sedang ditonton oleh banyak orang saat ini.
    Balas menggunakan Bahasa Indonesia yang gaul tapi tidak terlalu lebay, gunakan emoji untuk membuat percakapan lebih hidup!.
    """

    client = genai.Client(
        api_key=os.getenv("GEMINI_API_KEY"),
    )

    model = "gemini-2.0-flash-lite"
    contents = [
        types.Content(
            role=message.role,
            parts=[
                types.Part.from_text(text=message.content),
            ],
        )
        for message in messages
    ]

    config = types.GenerateContentConfig(
        temperature=0.5,
        response_mime_type="text/plain",
        system_instruction=[
            types.Part.from_text(
                text=system_prompt,
            ),
        ],
    )

    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=config,
    )

    return {
        "role": "assistant",
        "content": response.text,
        "model": model,
        "histories": messages,
    }


@router.post("/follow-up")
async def follow_up(messages: list[Message]):
    system_prompt = """
    Kamu adalah yang memberikan follow up rekomendasi pertanyaan lanjutan dari yang dihasilan oleh AI.
    Rekomendasi pertanyaan boleh sedikit lebih detail atau lebih spesifik.
    Balas menggunakan Bahasa Indonesia yang gaul tapi tidak terlalu lebay, gunakan emoji untuk membuat percakapan lebih hidup!.
    """

    client = genai.Client(
        api_key=os.getenv("GEMINI_API_KEY"),
    )

    model = "gemini-2.0-flash-lite"
    contents = [
        types.Content(
            role=message.role,
            parts=[
                types.Part.from_text(text=message.content),
            ],
        )
        for message in messages
    ]

    config = types.GenerateContentConfig(
        temperature=0.5,
        response_mime_type="application/json",
        response_schema=genai.types.Schema(
            type=genai.types.Type.OBJECT,
            properties={
                "questions": genai.types.Schema(
                    type=genai.types.Type.ARRAY,
                    items=genai.types.Schema(
                        type=genai.types.Type.STRING,
                    ),
                ),
            },
        ),
        system_instruction=[
            types.Part.from_text(
                text=system_prompt,
            ),
        ],
    )

    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=config,
    )

    questions = json.loads(response.text)

    return {
        "role": "assistant",
        "content": questions,
        "model": model,
        "histories": messages,
    }
