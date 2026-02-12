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
        cleanup_interval: float = 60.0,
        idle_ttl: float | None = None,
    ) -> None:
        self.min_interval = min_interval
        self.window = window
        self.max_requests = max_requests
        self.warn_interval = warn_interval
        self.cleanup_interval = cleanup_interval
        self.idle_ttl = idle_ttl or max(window, warn_interval, min_interval) * 12
        self._last_ts: dict[int, float] = {}
        self._recent: dict[int, deque] = {}
        self._last_warn: dict[int, float] = {}
        self._last_cleanup = 0.0

    async def __call__(self, handler, event, data):
        user = getattr(event, "from_user", None)
        if not user:
            return await handler(event, data)

        now = monotonic()
        self._cleanup_inactive_users(now)
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

    def _cleanup_inactive_users(self, now: float) -> None:
        if now - self._last_cleanup < self.cleanup_interval:
            return

        self._last_cleanup = now
        stale_before = now - self.idle_ttl
        all_user_ids = set(self._last_ts) | set(self._recent) | set(self._last_warn)

        for user_id in all_user_ids:
            dq = self._recent.get(user_id)
            last_recent = dq[-1] if dq else 0.0
            last_seen = max(
                self._last_ts.get(user_id, 0.0),
                self._last_warn.get(user_id, 0.0),
                last_recent,
            )
            if last_seen < stale_before:
                self._last_ts.pop(user_id, None)
                self._recent.pop(user_id, None)
                self._last_warn.pop(user_id, None)

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
