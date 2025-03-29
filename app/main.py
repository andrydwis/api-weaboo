from fastapi import FastAPI, HTTPException

from app.routers import manga

app = FastAPI()
app.include_router(manga.router, prefix="/manga", tags=["manga"])


@app.get("/")
async def root():
    return {"status": "ok", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)
