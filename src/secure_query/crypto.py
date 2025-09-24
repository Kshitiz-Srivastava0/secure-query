from __future__ import annotations

import base64
import json
from typing import Any, Dict

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

from .settings import settings

__all__ = [
    "ensure_keys",
    "get_public_key_pem",
    "decrypt_b64url_payload",
]


def ensure_keys() -> None:
    """Generate RSA keypair if missing."""
    if settings.private_key_file.exists() and settings.public_key_file.exists():
        return
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()

    settings.private_key_file.write_bytes(
        private_key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
    )
    settings.public_key_file.write_bytes(
        public_key.public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    )


def get_public_key_pem() -> str:
    return settings.public_key_file.read_text()


def _b64url_to_bytes(data: str) -> bytes:
    pad = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + pad)


def _load_private_key():
    return serialization.load_pem_private_key(
        settings.private_key_file.read_bytes(), password=None
    )


def decrypt_b64url_payload(ciphertext_b64url: str) -> Dict[str, Any]:
    """Decrypt base64url(RSA-OAEP(SHA256)) → dict"""
    ct = _b64url_to_bytes(ciphertext_b64url)
    pk = _load_private_key()
    pt = pk.decrypt(
        ct,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    result: Dict[str, Any] = json.loads(pt.decode("utf-8"))
    return result
