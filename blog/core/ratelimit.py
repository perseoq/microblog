import time
from collections import defaultdict, deque
from threading import Lock

_attempts = defaultdict(deque)
_lock = Lock()


def is_rate_limited(key, limit=10, window=300):
    now = time.time()
    with _lock:
        attempts = _attempts[key]
        while attempts and attempts[0] <= now - window:
            attempts.popleft()
        if len(attempts) >= limit:
            return True
        attempts.append(now)
        return False


def clear_rate_limit(key):
    with _lock:
        _attempts.pop(key, None)


def reset_rate_limits():
    with _lock:
        _attempts.clear()
