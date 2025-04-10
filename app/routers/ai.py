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
