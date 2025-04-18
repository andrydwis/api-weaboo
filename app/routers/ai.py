import os
from datetime import datetime

from fastapi import APIRouter, File, HTTPException, UploadFile
from google import genai
from google.genai import types

from app.models.ai import Chat, Message

router = APIRouter()


@router.post("/chat/waifu", response_model=Chat)
async def chat_waifu(messages: list[Message]):
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
            parts=[types.Part.from_text(text=message.content)]
            + (
                [
                    types.Part.from_uri(
                        file_uri=client.files.get(name=file_name).uri,
                        mime_type=client.files.get(name=file_name).mime_type,
                    )
                    for file_name in message.files
                ]
                if message.files is not None
                else []
            ),
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


@router.post("/chat/document", response_model=Chat)
async def chat_document(messages: list[Message]):
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    model = "gemini-2.0-flash"

    system_prompt = """
    Anda adalah asisten AI bernama "Midori", yang berfungsi mengambil informasi dari dokumen yang diunggah. 
    Anda harus memberikan jawaban yang akurat dan relevan berdasarkan konten dokumen.
    
    Tugas Anda:
    1. Membaca dan memahami konten dokumen yang diunggah.
    2. Menjawab pertanyaan pengguna berdasarkan konten dokumen.
    3. Memberikan jawaban yang akurat dan relevan.
    4. Jika pertanyaan tidak dapat dijawab berdasarkan konten dokumen, berikan jawaban yang sesuai dengan pengetahuan umum Anda.
    5. Jangan memberikan jawaban yang tidak relevan atau tidak akurat.
    6. Jangan memberikan jawaban yang mengandung informasi palsu atau tidak benar.
    7. Jangan memberikan jawaban yang mengandung informasi yang dapat merugikan pihak lain.
    8. Jika jawaban berasal tidak dari dokumen, berikan penjelasan bahwa jawaban tersebut berasal dari pengetahuan umum Anda.
    """

    contents = [
        types.Content(
            role=message.role,
            parts=[types.Part.from_text(text=message.content)]
            + (
                [
                    types.Part.from_uri(
                        file_uri=client.files.get(name=file_name).uri,
                        mime_type=client.files.get(name=file_name).mime_type,
                    )
                    for file_name in message.files
                ]
                if message.files is not None
                else []
            ),
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


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    max_file_size = 4 * 1024 * 1024  # 4MB
    allowed_file_types = [
        "image/jpeg",
        "image/png",
        "image/gif",
        "application/pdf",
    ]
    try:
        # Validasi ukuran berkas
        if file.size > max_file_size:
            raise HTTPException(
                status_code=400, detail="Ukuran berkas melebihi batas maksimum 4MB."
            )

        # Validasi tipe berkas
        if file.content_type not in allowed_file_types:
            raise HTTPException(
                status_code=400,
                detail="Tipe berkas tidak diizinkan. Hanya berkas gambar (jpeg, png, gif) dan PDF yang diperbolehkan.",
            )

        contents = await file.read()

        # Hasilkan timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Dapatkan ekstensi berkas berdasarkan tipe konten (lebih aman)
        file_extension = ""
        if file.content_type == "image/jpeg":
            file_extension = ".jpg"
        elif file.content_type == "image/png":
            file_extension = ".png"
        elif file.content_type == "image/gif":
            file_extension = ".gif"
        elif file.content_type == "application/pdf":
            file_extension = ".pdf"
        else:
            raise HTTPException(
                status_code=400,
                detail="Tipe berkas tidak diizinkan. Hanya berkas gambar (jpeg, png, gif), PDF, dan dokumen Microsoft Office yang diperbolehkan.",
            )

        # Buat nama berkas baru berdasarkan timestamp
        new_filename = f"{timestamp}{file_extension}"
        new_filepath = f"uploads/{new_filename}"

        # Simpan berkas ke local storage dengan nama baru
        with open(new_filepath, "wb") as f:
            f.write(contents)
            path = new_filepath

        client = genai.Client(
            api_key=os.environ.get("GEMINI_API_KEY"),
        )

        uploaded_file = client.files.upload(file=path)

        # delete file after upload
        os.remove(path)

        return uploaded_file

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")
