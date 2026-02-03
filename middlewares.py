from collections import deque
from time import monotonic

from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import CallbackQuery, Message


class RateLimitMiddleware(BaseMiddleware):
    def __init__(
        self,
        min_interval: float = 0.6,
        window: float = 10.0,
        max_requests: int = 8,
        warn_interval: float = 5.0,
    ) -> None:
        self.min_interval = min_interval
        self.window = window
        self.max_requests = max_requests
        self.warn_interval = warn_interval
        self._last_ts: dict[int, float] = {}
        self._recent: dict[int, deque] = {}
        self._last_warn: dict[int, float] = {}

    async def __call__(self, handler, event, data):
        user = getattr(event, "from_user", None)
        if not user:
            return await handler(event, data)

        now = monotonic()
        user_id = user.id

        last = self._last_ts.get(user_id)
        if last is not None and now - last < self.min_interval:
            return await self._throttle(event, user_id, now)

        self._last_ts[user_id] = now

        dq = self._recent.setdefault(user_id, deque())
        while dq and now - dq[0] > self.window:
            dq.popleft()
        dq.append(now)

        if len(dq) > self.max_requests:
            return await self._throttle(event, user_id, now)

        return await handler(event, data)

    async def _throttle(self, event, user_id: int, now: float):
        last_warn = self._last_warn.get(user_id, 0)
        if now - last_warn < self.warn_interval:
            return

        self._last_warn[user_id] = now
        message = "Слишком много запросов. Попробуйте чуть позже."

        if isinstance(event, CallbackQuery):
            try:
                await event.answer(message, show_alert=True)
            except Exception:
                pass
        elif isinstance(event, Message):
            try:
                await event.answer(message)
            except Exception:
                pass
