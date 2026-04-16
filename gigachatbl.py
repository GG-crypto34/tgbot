import os
from pathlib import Path
from typing import Any
from langchain_gigachat.chat_models import GigaChat
from dotenv import load_dotenv

def build_gigachat(config: dict[str, Any] = {}) -> GigaChat:
    load_dotenv()
    gc_cfg = config.get("gigachat", {})
    credentials = os.getenv("GIGACHAT_CREDENTIALS")
    scope = os.getenv("GIGACHAT_SCOPE")
    if not credentials:
        raise RuntimeError("Missing GIGACHAT_CREDENTIALS in environment")
    if not scope:
        raise RuntimeError("Missing GIGACHAT_SCOPE in environment")

    return GigaChat(
        credentials=credentials,
        scope=scope,
        model=gc_cfg.get("model", "GigaChat-2-Max"),
        temperature=float(gc_cfg.get("temperature", 0.2)),
        timeout=int(gc_cfg.get("timeout", 60)),
        verify_ssl_certs=bool(gc_cfg.get("verify_ssl_certs", False)),
    )


