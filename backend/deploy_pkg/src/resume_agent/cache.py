import os
from dotenv import load_dotenv

import hashlib

from src.resume_agent.redis import redis_client
from src.resume_agent.schemas import AnalyzeResumeResponse

load_dotenv()

CACHE_TTL_SECONDS = os.getenv(
    "CACHE_TTL_SECONDS"
)



def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    normalized = text.strip()
    return hashlib.sha256(
        normalized.encode("utf-8")
    ).hexdigest()


def build_analysis_cache_key(
    pdf_bytes: bytes,
    job_description: str,
) -> str:
    pdf_hash = sha256_bytes(pdf_bytes)
    jd_hash = sha256_text(job_description)

    return f"resume_analysis:{pdf_hash}:{jd_hash}"


async def get_cached_analysis(
    cache_key: str,
) -> AnalyzeResumeResponse | None:
    cached = await redis_client.get(cache_key)

    if cached is None:
        print("未命中 Redis 缓存:", cache_key)
        return None
    print("命中 Redis 缓存:", cache_key)
    return AnalyzeResumeResponse.model_validate_json(cached)


async def set_cached_analysis(
    cache_key: str,
    response: AnalyzeResumeResponse,
) -> None:
    await redis_client.set(
        cache_key,
        response.model_dump_json(),
        ex=CACHE_TTL_SECONDS,
    )