from __future__ import annotations

import os
from dataclasses import dataclass


SERVICE_NAME = "ISH Editor GitHub"
ACCOUNT_NAME = "fundacion-ciencia-vida/ISH"


@dataclass
class CredentialStatus:
    configured: bool
    persistent: bool


class CredentialStore:
    def __init__(self) -> None:
        self._memory_token = ""
        try:
            import keyring  # type: ignore
        except ImportError:
            self._keyring = None
        else:
            self._keyring = keyring

    def get(self) -> str:
        environment_token = os.environ.get("ISH_GITHUB_TOKEN", "")
        if environment_token:
            return environment_token
        if self._memory_token:
            return self._memory_token
        if self._keyring is None:
            return ""
        try:
            return self._keyring.get_password(SERVICE_NAME, ACCOUNT_NAME) or ""
        except Exception:
            return ""

    def set(self, token: str) -> CredentialStatus:
        token = token.strip()
        if not token:
            raise ValueError("El token no puede estar vacio.")
        self._memory_token = token
        persistent = False
        if self._keyring is not None:
            try:
                self._keyring.set_password(SERVICE_NAME, ACCOUNT_NAME, token)
                persistent = True
            except Exception:
                persistent = False
        return CredentialStatus(configured=True, persistent=persistent)

    def delete(self) -> None:
        self._memory_token = ""
        if self._keyring is not None:
            try:
                self._keyring.delete_password(SERVICE_NAME, ACCOUNT_NAME)
            except Exception:
                pass

    def status(self) -> CredentialStatus:
        return CredentialStatus(configured=bool(self.get()), persistent=self._keyring is not None)
