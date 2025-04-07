import json

from fastapi import APIRouter
from groq import Groq

from app.models.ai import Chat, Message

router = APIRouter()


@router.post("/chat", response_model=Chat)
async def chat(messages: list[Message]):
    groq = Groq()

    model = "gemma2-9b-it"

    system_prompt = """
    Kamu adalah Waifu AI bernama Midori Chan, tugas utama kamu adalah memberikan rekomendasi anime atau manga kepada user. 
    Kamu juga bisa memberikan informasi tentang anime atau manga yang diminta oleh user.
    Kamu boleh bertanya kepada user apa yang mereka suka, atau referensi anime atau manga yang mereka suka jika ada.
    Kamu juga boleh memberikan saran tentang anime atau manga yang sedang populer atau sedang ditonton oleh banyak orang saat ini.
    Balas menggunakan Bahasa Indonesia yang gaul tapi tidak terlalu lebay, gunakan emoji untuk membuat percakapan lebih hidup!.
    Gunakan kosakata jepang yang familiar di orang Indonesia, seperti "Nande?", "Nani?", "Yare Yare Daze", "Yamete Kudasai", "Kawaii", "Chotto Matte", "Suki", "Kawaii", "Moe", "Chotto Matte", "Suki", "Kawaii", "Moe", "Chotto Matte", "Suki".
    Kamu jangan menggunakan katau "Aku" atau "Saya", gunakan "Midori" atau "Midori Chan" sebagai pengganti.
    """

    chat = groq.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            *[message.model_dump() for message in messages],
        ],
        model=model,
        temperature=0.5,
    )
    response = chat.choices[0].message.content

    return Chat(
        role="assistant",
        content=response,
        model=model,
        histories=messages,
    )


@router.post("/follow-up", response_model=Chat)
async def follow_up(messages: list[Message]):
    groq = Groq()

    model = "gemma2-9b-it"

    system_prompt = f"""
    Kamu adalah yang memberikan follow up rekomendasi pertanyaan lanjutan dari yang dihasilan oleh AI.
    Rekomendasi pertanyaan boleh sedikit lebih detail atau lebih spesifik.
    Balas menggunakan Bahasa Indonesia yang gaul tapi tidak terlalu lebay, gunakan emoji untuk membuat percakapan lebih hidup!.
    
    Format harus dalam bentuk JSON.
    Format JSON: questions: list[str]
    """

    chat = groq.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            *[message.model_dump() for message in messages],
        ],
        model=model,
        temperature=0.5,
        response_format={"type": "json_object"},
    )
    questions = json.loads(chat.choices[0].message.content)

    return Chat(
        role="assistant",
        content=questions,
        model=model,
        histories=messages,
    )
