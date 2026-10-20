import runpy
from pathlib import Path

import pytest

PRODUCTION = Path(__file__).parents[1] / "environments" / "production.py"


def load_production():
    return runpy.run_path(str(PRODUCTION))


@pytest.mark.parametrize("value", ["False", "false", "0", ""])
def test_debug_off_for_falsy_values(monkeypatch, value):
    monkeypatch.setenv("DEBUG", value)
    assert load_production()["DEBUG"] is False


def test_debug_off_when_unset(monkeypatch):
    monkeypatch.delenv("DEBUG", raising=False)
    assert load_production()["DEBUG"] is False


def test_debug_on_only_for_true(monkeypatch):
    monkeypatch.setenv("DEBUG", "True")
    assert load_production()["DEBUG"] is True


def test_allowed_hosts_default_to_host(monkeypatch):
    monkeypatch.delenv("ALLOWED_HOSTS", raising=False)
    monkeypatch.setenv("HOST", "report.local")
    assert load_production()["ALLOWED_HOSTS"] == ["report.local"]


def test_allowed_hosts_from_env(monkeypatch):
    monkeypatch.setenv("ALLOWED_HOSTS", "a.example, b.example")
    assert load_production()["ALLOWED_HOSTS"] == ["a.example", "b.example"]
