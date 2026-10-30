import threading
from collections import deque
from datetime import datetime, timezone

MAX_EVENTS = 100

class ActivityLog:
    """Recent moves and errors, kept in memory and shared between threads."""

    def __init__(self, max_events=MAX_EVENTS, clock=None):
        self._events = deque(maxlen=max_events)
        self._lock = threading.Lock()
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    def record_move(self, source, destination):
        self._add({
            "timestamp": self._timestamp(),
            "type": "moved",
            "source": str(source),
            "destination": str(destination),
        })

    def record_error(self, source, message):
        self._add({
            "timestamp": self._timestamp(),
            "type": "error",
            "source": str(source),
            "message": message,
        })

    def events(self):
        """Return events newest first."""
        with self._lock:
            return list(reversed(self._events))

    def _add(self, event):
        with self._lock:
            self._events.append(event)

    def _timestamp(self):
        return self._clock().isoformat()
