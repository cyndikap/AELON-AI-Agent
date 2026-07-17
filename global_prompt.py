# -*- coding: utf-8 -*-
from pathlib import Path

_GLOBAL_PROMPT = None

def _load() -> str:
    global _GLOBAL_PROMPT
    if _GLOBAL_PROMPT is None:
        path = Path(__file__).resolve().parent / "global_prompt.txt"
        _GLOBAL_PROMPT = path.read_text(encoding="utf-8").strip()
    return _GLOBAL_PROMPT

def prepend(prompt: str) -> str:
    """Préfixe le prompt avec les règles globales AELON."""
    return f"{_load()}\n\n{prompt}"
