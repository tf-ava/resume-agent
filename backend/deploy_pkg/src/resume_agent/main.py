from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.resume_agent.api.resume_analyze import router


app = FastAPI(
    title="Resume Analysis Agent"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://tf-ava.github.io"
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/health")
async def health():
    return {"status": "ok"}