import os
from dotenv import load_dotenv

import redis.asyncio as redis


load_dotenv()

REDIS_URL = os.getenv(
    "REDIS_URL"
)

redis_client = None

if REDIS_URL:
    redis_client = redis.from_url(
        REDIS_URL,
        encoding="utf-8",
        decode_responses=True
    )

