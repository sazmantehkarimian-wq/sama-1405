"""Bounded retries for short SQLite write transactions under LAN contention."""
from functools import wraps
import time

from django.db import OperationalError, close_old_connections


def retry_locked(function):
    @wraps(function)
    def wrapped(*args, **kwargs):
        for attempt in range(7):
            try:
                return function(*args, **kwargs)
            except OperationalError as exc:
                if "locked" not in str(exc).lower() or attempt == 6:
                    raise
                close_old_connections()
                time.sleep(0.05 * (attempt + 1))
    return wrapped
