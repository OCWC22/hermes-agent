"""Helpers for account-qualified gateway adapter identities."""

import re
from typing import Any

_ACCOUNT_RE = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*$")
_SUFFIX_RE = re.compile(r"^[A-Z0-9]+(?:_[A-Z0-9]+)*$")


def make_adapter_key(platform: Any, account_name: str = "default") -> str:
    """Build the stable adapter key for a platform/account pair."""
    platform_name = str(getattr(platform, "value", platform))
    account = str(account_name or "default").strip().lower()
    if account == "default":
        return platform_name
    if not _ACCOUNT_RE.fullmatch(account):
        raise ValueError(f"Invalid adapter account name: {account_name!r}")
    return f"{platform_name}:{account}"


def parse_adapter_key(adapter_key: str) -> tuple[str, str]:
    """Return ``(platform, account_name)`` for an adapter key."""
    key = str(adapter_key or "").strip()
    if ":" not in key:
        return key, "default"
    platform, account = key.split(":", 1)
    return platform, account or "default"


def normalize_telegram_account_suffix(suffix: str) -> str:
    """Normalize a TELEGRAM_BOT_TOKEN_<SUFFIX> suffix to an account name."""
    raw = str(suffix or "").strip()
    if not _SUFFIX_RE.fullmatch(raw):
        raise ValueError(f"Malformed Telegram bot token suffix {suffix!r}")
    account = raw.lower()
    if account == "default":
        raise ValueError("TELEGRAM_BOT_TOKEN_DEFAULT is reserved; use TELEGRAM_BOT_TOKEN")
    return account
