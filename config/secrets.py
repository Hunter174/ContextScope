import json
import os
from pathlib import Path
from typing import Optional
from config.paths import CONFIG_DIR
from cryptography.fernet import Fernet, InvalidToken

SECRETS_FILE = CONFIG_DIR / "secrets.json"
KEY_FILE = CONFIG_DIR / "secret.key"
KEY_ENV = "CONTEXTSCOPE_SECRET_KEY"


def _ensure_key() -> str:
    key = os.getenv(KEY_ENV)
    if key:
        return key

    # Load existing key file if present
    if KEY_FILE.exists():
        return KEY_FILE.read_text().strip()

    # Generate and persist a new key by default
    KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
    new_key = Fernet.generate_key().decode()
    KEY_FILE.write_text(new_key)
    return new_key


KEY = _ensure_key()
FERNET = Fernet(KEY.encode())


def _load_all():
    if not SECRETS_FILE.exists():
        return {}
    try:
        return json.loads(SECRETS_FILE.read_text())
    except Exception:
        return {}


def _save_all(data: dict):
    SECRETS_FILE.parent.mkdir(parents=True, exist_ok=True)
    SECRETS_FILE.write_text(json.dumps(data, indent=2))


class SecretStore:
    """File-backed secret store with default Fernet encryption.

    - If CONTEXTSCOPE_SECRET_KEY is set, it is used.
    - Otherwise a key is generated and stored at secret.key on first use.
    """

    SERVICE_NAME = "ContextScope"

    @classmethod
    def save(cls, key: str, value: Optional[str]):
        if value is None:
            return
        data = _load_all()
        value_enc = FERNET.encrypt(value.encode()).decode()
        data[key] = value_enc
        _save_all(data)

    @classmethod
    def load(cls, key: str) -> Optional[str]:
        data = _load_all()
        val = data.get(key)
        if val is None:
            return None
        try:
            return FERNET.decrypt(val.encode()).decode()
        except InvalidToken:
            # If legacy plaintext exists, return it so users can migrate
            return val
        except Exception:
            return None

    @classmethod
    def delete(cls, key: str):
        data = _load_all()
        if key in data:
            data.pop(key)
            _save_all(data)
