from __future__ import annotations

import os
from pathlib import Path

DEFAULT_KEYS_DIR = Path(os.environ.get("SECURE_QUERY_KEYS_DIR", "keys")).resolve()


class Settings:
    keys_dir: Path = DEFAULT_KEYS_DIR
    private_key_file: Path
    public_key_file: Path

    def __init__(self, keys_dir: Path | str | None = None):
        if keys_dir is not None:
            self.keys_dir = Path(keys_dir).resolve()
        else:
            self.keys_dir = DEFAULT_KEYS_DIR
        self.keys_dir.mkdir(parents=True, exist_ok=True)
        self.private_key_file = self.keys_dir / "private_key.pem"
        self.public_key_file = self.keys_dir / "public_key.pem"


settings = Settings()
