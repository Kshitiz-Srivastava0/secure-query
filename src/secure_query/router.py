from __future__ import annotations

import time
from collections import defaultdict
from typing import DefaultDict, List

from fastapi import APIRouter, HTTPException, Query, Request

from .crypto import decrypt_b64url_payload, ensure_keys, get_public_key_pem

router = APIRouter(prefix="/secure-query", tags=["Secure Query"])

# Rate limiting (in-memory, replace with Redis for production)
_rate_limit_storage: DefaultDict[str, List[float]] = defaultdict(list)
DECRYPT_RATE_LIMIT = 10  # requests per minute
RATE_LIMIT_WINDOW = 60  # seconds


def _check_rate_limit(client_ip: str) -> bool:
    """Check if client has exceeded rate limit for decrypt endpoint."""
    now = time.time()
    # Clean old entries
    _rate_limit_storage[client_ip] = [
        timestamp
        for timestamp in _rate_limit_storage[client_ip]
        if now - timestamp < RATE_LIMIT_WINDOW
    ]

    # Check limit
    if len(_rate_limit_storage[client_ip]) >= DECRYPT_RATE_LIMIT:
        return False

    # Record this request
    _rate_limit_storage[client_ip].append(now)
    return True


# Ensure keys exist at import time (safe/idempotent)
ensure_keys()


@router.get("/public-key")
def public_key():
    """Expose PEM public key for the browser (RSA-OAEP-256)."""
    return {"alg": "RSA-OAEP-256", "format": "spki-pem", "pem": get_public_key_pem()}


@router.get("/decrypt")
def decrypt(
    request: Request,
    data: str = Query(
        ..., description="base64url RSA-OAEP ciphertext", max_length=4096
    ),
):
    # Rate limiting check
    client_ip = request.client.host if request.client else "unknown"
    if not _check_rate_limit(client_ip):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    try:
        payload = decrypt_b64url_payload(data)
        return {"ok": True, "payload": payload}
    except Exception:
        raise HTTPException(status_code=400, detail="Decryption failed")
