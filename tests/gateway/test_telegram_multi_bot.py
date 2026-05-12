"""Tests for local multi-Telegram-bot gateway configuration."""

import pytest

from gateway.config import load_telegram_accounts_from_env
from gateway.delivery import DeliveryTarget


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
