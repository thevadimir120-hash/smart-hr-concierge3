from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable
from typing import TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


async def async_retry(
    func: Callable[[], Awaitable[T]],
    *,
    attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple[type[BaseException], ...] = (Exception,),
) -> T:
    last_error: BaseException | None = None
    wait = delay
    for attempt in range(1, attempts + 1):
        try:
            return await func()
        except exceptions as exc:
            last_error = exc
            if attempt == attempts:
                break
            logger.warning(
                "Retry %s/%s after error: %s",
                attempt,
                attempts,
                exc,
            )
            await asyncio.sleep(wait)
            wait *= backoff
    assert last_error is not None
    raise last_error
