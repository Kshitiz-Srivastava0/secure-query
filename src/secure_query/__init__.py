from .crypto import decrypt_b64url_payload, ensure_keys, get_public_key_pem

try:
    # Optional import (only if FastAPI installed)
    from .router import router  # type: ignore
except Exception:  # pragma: no cover
    router = None  # type: ignore

__all__ = [
    "ensure_keys",
    "get_public_key_pem",
    "decrypt_b64url_payload",
    "router",
]
