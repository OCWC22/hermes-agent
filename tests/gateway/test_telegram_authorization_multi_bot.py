"""Authorization tests for account-qualified Telegram gateway adapters."""

from types import SimpleNamespace
from unittest.mock import MagicMock

from gateway.config import Platform, PlatformConfig
from gateway.run import GatewayRunner
from gateway.session import SessionSource


def _runner_with_telegram_adapters(**adapter_extras):
    runner = object.__new__(GatewayRunner)
    runner.adapters = {}
    for adapter_key, extra in adapter_extras.items():
        runner.adapters[adapter_key] = SimpleNamespace(
            config=PlatformConfig(enabled=True, adapter_key=adapter_key, extra=extra),
            platform=Platform.TELEGRAM,
            adapter_key=adapter_key,
        )
    runner.pairing_store = MagicMock()
    runner.pairing_store.is_approved.return_value = False
    return runner


def _source(adapter_key, user_id, chat_type="dm", chat_id="123"):
    return SessionSource(
        platform=Platform.TELEGRAM,
        adapter_key=adapter_key,
        chat_id=chat_id,
        chat_type=chat_type,
        user_id=user_id,
    )


def test_telegram_named_accounts_enforce_separate_allowed_users(monkeypatch):
    monkeypatch.delenv("TELEGRAM_ALLOWED_USERS", raising=False)
    runner = _runner_with_telegram_adapters(
        **{
            "telegram:ceo": {"allowed_users": "111"},
            "telegram:research": {"allowed_users": "222"},
        }
    )

    assert runner._is_user_authorized(_source("telegram:ceo", "111")) is True
    assert runner._is_user_authorized(_source("telegram:ceo", "222")) is False
    assert runner._is_user_authorized(_source("telegram:research", "222")) is True
    assert runner._is_user_authorized(_source("telegram:research", "111")) is False


def test_telegram_named_env_allowlist_does_not_inherit_default(monkeypatch):
    monkeypatch.setenv("TELEGRAM_ALLOWED_USERS", "111")
    monkeypatch.setenv("TELEGRAM_ALLOWED_USERS_RESEARCH", "222")
    runner = _runner_with_telegram_adapters(**{"telegram:research": {}})

    assert runner._is_user_authorized(_source("telegram:research", "222")) is True
    assert runner._is_user_authorized(_source("telegram:research", "111")) is False


def test_telegram_default_allowlist_behavior_remains_unchanged(monkeypatch):
    monkeypatch.setenv("TELEGRAM_ALLOWED_USERS", "111")
    runner = _runner_with_telegram_adapters(telegram={})

    assert runner._is_user_authorized(_source("telegram", "111")) is True
    assert runner._is_user_authorized(_source("telegram", "222")) is False


def test_telegram_group_allowlists_are_adapter_specific(monkeypatch):
    monkeypatch.delenv("TELEGRAM_GROUP_ALLOWED_CHATS", raising=False)
    monkeypatch.delenv("TELEGRAM_GROUP_ALLOWED_USERS", raising=False)
    runner = _runner_with_telegram_adapters(
        **{
            "telegram:ceo": {
                "group_allowed_chats": "ceo-chat",
                "group_allowed_users": "111",
            },
            "telegram:research": {
                "group_allowed_chats": "research-chat",
                "group_allowed_users": "222",
            },
        }
    )

    assert runner._is_user_authorized(_source("telegram:ceo", "111", "group", "ceo-chat")) is True
    assert runner._is_user_authorized(_source("telegram:ceo", "222", "group", "ceo-chat")) is False
    assert runner._is_user_authorized(_source("telegram:ceo", "111", "group", "research-chat")) is False
    assert runner._is_user_authorized(_source("telegram:research", "222", "group", "research-chat")) is True
    assert runner._is_user_authorized(_source("telegram:research", "111", "group", "research-chat")) is False
