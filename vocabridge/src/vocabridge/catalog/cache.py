"""A tiny file cache so repeated searches do not re-query public services."""

from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path


def default_cache_dir() -> Path:
    if os.environ.get("VOCABRIDGE_CACHE_DIR"):
        return Path(os.environ["VOCABRIDGE_CACHE_DIR"])
    xdg = os.environ.get("XDG_CACHE_HOME")
    return (Path(xdg) if xdg else Path.home() / ".cache") / "vocabridge"


class FileCache:
    def __init__(self, directory: str | Path | None = None, ttl_seconds: int = 7 * 24 * 3600):
        self.directory = Path(directory) if directory else default_cache_dir()
        self.ttl_seconds = ttl_seconds

    def _path(self, namespace: str, key: str) -> Path:
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:32]
        return self.directory / namespace / f"{digest}.json"

    def get(self, namespace: str, key: str):
        path = self._path(namespace, key)
        if not path.exists():
            return None
        if self.ttl_seconds and time.time() - path.stat().st_mtime > self.ttl_seconds:
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None

    def set(self, namespace: str, key: str, value) -> None:
        path = self._path(namespace, key)
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(value), encoding="utf-8")
        except OSError:
            pass  # caching is best-effort
