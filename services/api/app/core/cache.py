from redis.asyncio import Redis


async def get_redis_ping(redis_url: str) -> bool:
    client = Redis.from_url(redis_url)
    try:
        return await client.ping()
    except Exception:
        return False
    finally:
        await client.aclose()
