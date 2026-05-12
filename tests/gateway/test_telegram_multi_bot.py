"""Tests for local multi-Telegram-bot gateway configuration."""

import os

import pytest

from gateway.config import GatewayConfig, Platform, load_telegram_accounts_from_env
from gateway.delivery import DeliveryTarget
from gateway.run import GatewayRunner
from gateway.session import SessionSource


@pytest.fixture(autouse=True)
def clear_telegram_env(monkeypatch):
    for key in list(os.environ):
        if key.startswith("TELEGRAM_"):
            monkeypatch.delenv(key, raising=False)



def test_load_telegram_accounts_default_only(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "default-token")

    accounts = load_telegram_accounts_from_env()

    assert len(accounts) == 1
    assert accounts[0].account_name == "default"
    assert accounts[0].adapter_key == "telegram"
    assert accounts[0].bot_token == "default-token"


def test_load_telegram_accounts_from_env_default_and_named(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "default-token")
    monkeypatch.setenv("TELEGRAM_ALLOWED_USERS", "1")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN_CEO", "ceo-token")
    monkeypatch.setenv("TELEGRAM_ALLOWED_USERS_CEO", "2")
    monkeypatch.setenv("TELEGRAM_HOME_CHANNEL_CEO", "123")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN_RESEARCH", "research-token")

    accounts = load_telegram_accounts_from_env()

    assert [account.account_name for account in accounts] == ["default", "ceo", "research"]
    assert [account.adapter_key for account in accounts] == ["telegram", "telegram:ceo", "telegram:research"]
    assert accounts[0].allowed_users == "1"
    assert accounts[1].allowed_users == "2"
    assert accounts[1].home_channel == "123"


def test_load_telegram_accounts_rejects_duplicate_tokens(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "same-token")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN_INFRA", "same-token")

    with pytest.raises(ValueError, match="Duplicate Telegram bot token configured"):
        load_telegram_accounts_from_env()


def test_outbound_route_resolves_account_adapter_key():
    target = DeliveryTarget.parse("telegram:ceo:123456789")

    assert target.adapter_key == "telegram:ceo"
    assert target.chat_id == "123456789"


def test_load_telegram_accounts_named_only(monkeypatch):
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN_CEO", "ceo-token")

    accounts = load_telegram_accounts_from_env()

    assert [account.adapter_key for account in accounts] == ["telegram:ceo"]
    assert accounts[0].account_name == "ceo"


def test_load_telegram_accounts_normalizes_suffix(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN_CEO__TEAM", "ceo-team-token")
    monkeypatch.setenv("TELEGRAM_ALLOWED_USERS_CEO__TEAM", "42")

    accounts = load_telegram_accounts_from_env()

    assert accounts[0].account_name == "ceo_team"
    assert accounts[0].adapter_key == "telegram:ceo_team"
    assert accounts[0].allowed_users == "42"


def test_load_telegram_accounts_rejects_default_suffix(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN_DEFAULT", "ambiguous-token")

    with pytest.raises(ValueError, match="TELEGRAM_BOT_TOKEN_DEFAULT is ambiguous"):
        load_telegram_accounts_from_env()


def test_load_telegram_accounts_account_webhook_fields(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN_CEO", "ceo-token")
    monkeypatch.setenv("TELEGRAM_WEBHOOK_URL_CEO", "https://example.com/telegram/ceo")
    monkeypatch.setenv("TELEGRAM_WEBHOOK_PORT_CEO", "9001")
    monkeypatch.setenv("TELEGRAM_WEBHOOK_SECRET_CEO", "secret")

    account = load_telegram_accounts_from_env()[0]

    assert account.webhook_url == "https://example.com/telegram/ceo"
    assert account.webhook_port == "9001"
    assert account.webhook_secret == "secret"


def test_load_telegram_accounts_rejects_partial_multi_webhook(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "default-token")
    monkeypatch.setenv("TELEGRAM_WEBHOOK_URL", "https://example.com/telegram")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN_CEO", "ceo-token")

    with pytest.raises(ValueError, match="requires account-specific webhook config"):
        load_telegram_accounts_from_env()


def test_load_telegram_accounts_rejects_multi_webhook_same_port(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN_CEO", "ceo-token")
    monkeypatch.setenv("TELEGRAM_WEBHOOK_URL_CEO", "https://example.com/telegram/ceo")
    monkeypatch.setenv("TELEGRAM_WEBHOOK_PORT_CEO", "9001")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN_RESEARCH", "research-token")
    monkeypatch.setenv("TELEGRAM_WEBHOOK_URL_RESEARCH", "https://example.com/telegram/research")
    monkeypatch.setenv("TELEGRAM_WEBHOOK_PORT_RESEARCH", "9001")

    with pytest.raises(ValueError, match="requires unique account-specific webhook ports"):
        load_telegram_accounts_from_env()


def test_iter_platform_configs_yields_default_and_named(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "default-token")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN_CEO", "ceo-token")
    runner = object.__new__(GatewayRunner)
    runner.config = GatewayConfig()

    configs = runner._iter_platform_configs()

    assert [key for key, _, _ in configs] == ["telegram", "telegram:ceo"]
    assert [cfg.token for _, platform, cfg in configs if platform == Platform.TELEGRAM] == ["default-token", "ceo-token"]


def test_account_specific_allowlists_are_enforced(monkeypatch):
    monkeypatch.setenv("TELEGRAM_ALLOWED_USERS_CEO", "user-a")
    monkeypatch.setenv("TELEGRAM_ALLOWED_USERS_RESEARCH", "user-b")
    runner = object.__new__(GatewayRunner)
    runner.adapters = {}
    runner.pairing_store = type("Pairing", (), {"is_approved": lambda self, platform, user_id: False})()

    ceo_user = SessionSource(platform=Platform.TELEGRAM, chat_id="1", user_id="user-a", adapter_key="telegram:ceo")
    research_user = SessionSource(platform=Platform.TELEGRAM, chat_id="1", user_id="user-b", adapter_key="telegram:research")

    assert runner._is_user_authorized(ceo_user) is True
    assert runner._is_user_authorized(research_user) is True
    assert runner._is_user_authorized(SessionSource(platform=Platform.TELEGRAM, chat_id="1", user_id="user-a", adapter_key="telegram:research")) is False
    assert runner._is_user_authorized(SessionSource(platform=Platform.TELEGRAM, chat_id="1", user_id="user-b", adapter_key="telegram:ceo")) is False


def test_account_specific_group_allowlists_are_enforced(monkeypatch):
    monkeypatch.setenv("TELEGRAM_GROUP_ALLOWED_USERS_CEO", "user-a")
    monkeypatch.setenv("TELEGRAM_GROUP_ALLOWED_CHATS_CEO", "-100")
    runner = object.__new__(GatewayRunner)
    runner.adapters = {}
    runner.pairing_store = type("Pairing", (), {"is_approved": lambda self, platform, user_id: False})()

    allowed = SessionSource(platform=Platform.TELEGRAM, chat_id="-100", chat_type="group", user_id="user-a", adapter_key="telegram:ceo")
    wrong_chat = SessionSource(platform=Platform.TELEGRAM, chat_id="-200", chat_type="group", user_id="user-a", adapter_key="telegram:ceo")
    wrong_user = SessionSource(platform=Platform.TELEGRAM, chat_id="-100", chat_type="group", user_id="user-b", adapter_key="telegram:ceo")

    assert runner._is_user_authorized(allowed) is True
    assert runner._is_user_authorized(wrong_chat) is False
    assert runner._is_user_authorized(wrong_user) is False
