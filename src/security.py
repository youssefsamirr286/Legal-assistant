"""Input sanitization and safety helpers for user-facing legal queries."""

from __future__ import annotations

import re

MAX_INPUT_LENGTH = 4000

_INJECTION_PATTERNS = [
    r"(?i)ignore\s+(all\s+)?(previous|prior)\s+instructions",
    r"(?i)disregard\s+(the\s+)?system\s+prompt",
    r"(?i)you\s+are\s+now\s+(a\s+)?(?:dan|jailbreak)",
]


def sanitize_user_input(text: str) -> str:
    """Strip, cap length, and flag common prompt-injection phrases."""
    cleaned = (text or "").strip()
    if not cleaned:
        return ""

    cleaned = cleaned[:MAX_INPUT_LENGTH]

    for pattern in _INJECTION_PATTERNS:
        if re.search(pattern, cleaned):
            cleaned = re.sub(pattern, "[filtered]", cleaned)

    return cleaned
