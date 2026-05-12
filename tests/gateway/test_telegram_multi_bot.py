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


def test_telegram_bot_token_default_is_rejected(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN_DEFAULT", "default-token")

    with pytest.raises(ValueError, match="TELEGRAM_BOT_TOKEN_DEFAULT"):
        load_telegram_accounts_from_env()


def test_malformed_telegram_account_suffix_is_rejected(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN__BAD", "bad-token")

    with pytest.raises(ValueError, match="Malformed Telegram bot token suffix"):
        load_telegram_accounts_from_env()


def test_multi_account_shared_webhook_port_fails(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN_CEO", "ceo-token")
    monkeypatch.setenv("TELEGRAM_WEBHOOK_URL_CEO", "https://example.com/telegram/ceo")
    monkeypatch.setenv("TELEGRAM_WEBHOOK_PORT_CEO", "8443")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN_RESEARCH", "research-token")
    monkeypatch.setenv("TELEGRAM_WEBHOOK_URL_RESEARCH", "https://example.com/telegram/research")
    monkeypatch.setenv("TELEGRAM_WEBHOOK_PORT_RESEARCH", "8443")

    with pytest.raises(ValueError, match="unique local ports"):
        load_telegram_accounts_from_env()


def test_multi_account_unique_webhook_ports_pass(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN_CEO", "ceo-token")
    monkeypatch.setenv("TELEGRAM_WEBHOOK_URL_CEO", "https://example.com/telegram/ceo")
    monkeypatch.setenv("TELEGRAM_WEBHOOK_PORT_CEO", "8443")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN_RESEARCH", "research-token")
    monkeypatch.setenv("TELEGRAM_WEBHOOK_URL_RESEARCH", "https://example.com/telegram/research")
    monkeypatch.setenv("TELEGRAM_WEBHOOK_PORT_RESEARCH", "8444")

    accounts = load_telegram_accounts_from_env()

    assert [account.adapter_key for account in accounts] == ["telegram:ceo", "telegram:research"]
