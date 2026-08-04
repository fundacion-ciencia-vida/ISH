from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import re
import secrets
import threading
import time
from pathlib import Path

from .config import CONFIG_DIR


AUTH_FILE = CONFIG_DIR / "auth.json"
AUTH_COOKIE = "ish_editor_auth"
PASSWORD_ITERATIONS = 310_000
SESSION_TTL_SECONDS = 12 * 60 * 60
LOGIN_MAX_FAILURES = 5
LOGIN_LOCK_SECONDS = 60
USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9._-]{3,64}$")


class LocalAuthError(ValueError):
    pass


class LocalCredentialStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or AUTH_FILE

    @property
    def configured(self) -> bool:
        return self._load() is not None

    def _load(self) -> dict[str, object] | None:
        if not self.path.exists():
            return None
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None
        required = {"version", "username", "salt", "password_hash", "iterations"}
        return payload if isinstance(payload, dict) and required.issubset(payload) else None

    def setup(self, username: str, password: str) -> None:
        if self.configured:
            raise LocalAuthError("Las credenciales locales ya fueron configuradas.")
        self._write(username, password)

    def change_password(self, current_password: str, new_password: str) -> str:
        payload = self._load()
        if payload is None:
            raise LocalAuthError("Las credenciales locales no estan configuradas.")
        username = str(payload["username"])
        if not self.verify(username, current_password):
            raise LocalAuthError("La contrasena actual no es correcta.")
        if hmac.compare_digest(current_password, new_password):
            raise LocalAuthError("La nueva contrasena debe ser distinta de la actual.")
        self._write(username, new_password)
        return username

    def reset(self) -> bool:
        if not self.path.exists():
            return False
        self.path.unlink()
        return True

    def _write(self, username: str, password: str) -> None:
        clean_username = username.strip()
        if not USERNAME_PATTERN.fullmatch(clean_username):
            raise LocalAuthError("El usuario debe tener entre 3 y 64 caracteres simples.")
        if len(password) < 10:
            raise LocalAuthError("La contrasena debe tener al menos 10 caracteres.")
        if len(password) > 256:
            raise LocalAuthError("La contrasena es demasiado extensa.")

        salt = secrets.token_bytes(32)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PASSWORD_ITERATIONS)
        payload = {
            "version": 1,
            "username": clean_username,
            "salt": base64.b64encode(salt).decode("ascii"),
            "password_hash": base64.b64encode(digest).decode("ascii"),
            "iterations": PASSWORD_ITERATIONS,
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_name(f".{self.path.name}.{secrets.token_hex(6)}.tmp")
        temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if os.name != "nt":
            temporary.chmod(0o600)
        temporary.replace(self.path)

    def verify(self, username: str, password: str) -> bool:
        payload = self._load()
        if payload is None:
            return False
        try:
            salt = base64.b64decode(str(payload["salt"]), validate=True)
            expected = base64.b64decode(str(payload["password_hash"]), validate=True)
            iterations = int(payload["iterations"])
        except (KeyError, TypeError, ValueError):
            return False
        supplied = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
        username_matches = hmac.compare_digest(username.strip(), str(payload["username"]))
        return username_matches and hmac.compare_digest(supplied, expected)


class LocalSessionStore:
    def __init__(self, ttl_seconds: int = SESSION_TTL_SECONDS) -> None:
        self.ttl_seconds = ttl_seconds
        self._sessions: dict[str, float] = {}
        self._lock = threading.Lock()

    def create(self) -> str:
        token = secrets.token_urlsafe(32)
        with self._lock:
            self._purge_locked()
            self._sessions[token] = time.time() + self.ttl_seconds
        return token

    def valid(self, token: str) -> bool:
        if not token:
            return False
        with self._lock:
            self._purge_locked()
            expires = self._sessions.get(token, 0)
            return expires > time.time()

    def revoke(self, token: str) -> None:
        if not token:
            return
        with self._lock:
            self._sessions.pop(token, None)

    def revoke_all(self) -> None:
        with self._lock:
            self._sessions.clear()

    def _purge_locked(self) -> None:
        now = time.time()
        expired = [token for token, expires in self._sessions.items() if expires <= now]
        for token in expired:
            self._sessions.pop(token, None)


class LocalLoginLimiter:
    def __init__(self, max_failures: int = LOGIN_MAX_FAILURES, lock_seconds: int = LOGIN_LOCK_SECONDS) -> None:
        self.max_failures = max_failures
        self.lock_seconds = lock_seconds
        self._attempts: dict[str, tuple[int, float]] = {}
        self._lock = threading.Lock()

    def retry_after(self, key: str) -> int:
        with self._lock:
            count, locked_until = self._attempts.get(key, (0, 0))
            remaining = max(0, int(locked_until - time.time() + 0.999))
            if not remaining and locked_until:
                self._attempts.pop(key, None)
            return remaining if count >= self.max_failures else 0

    def failed(self, key: str) -> int:
        with self._lock:
            count, locked_until = self._attempts.get(key, (0, 0))
            now = time.time()
            if locked_until > now:
                return max(1, int(locked_until - now + 0.999))
            count += 1
            if count >= self.max_failures:
                locked_until = now + self.lock_seconds
            else:
                locked_until = 0
            self._attempts[key] = (count, locked_until)
            if len(self._attempts) > 512:
                self._attempts = dict(list(self._attempts.items())[-256:])
            return max(0, int(locked_until - now + 0.999))

    def clear(self, key: str) -> None:
        with self._lock:
            self._attempts.pop(key, None)
