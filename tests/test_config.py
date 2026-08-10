import pytest
from shared.utils.config import get_env, get_env_int, get_env_list


class TestGetEnv:
    def test_returns_value(self, monkeypatch: object) -> None:
        monkeypatch.setenv("MY_KEY", "hello")  # type: ignore[attr-defined]
        assert get_env("MY_KEY") == "hello"

    def test_raises_when_missing(self) -> None:
        with pytest.raises(RuntimeError, match="MISSING_KEY"):
            get_env("MISSING_KEY")

    def test_returns_default_when_missing(self) -> None:
        assert get_env("MISSING_KEY", "fallback") == "fallback"

    def test_ignores_default_when_set(self, monkeypatch: object) -> None:
        monkeypatch.setenv("MY_KEY", "val")  # type: ignore[attr-defined]
        assert get_env("MY_KEY", "fallback") == "val"


class TestGetEnvInt:
    def test_returns_int(self, monkeypatch: object) -> None:
        monkeypatch.setenv("PORT", "8080")  # type: ignore[attr-defined]
        assert get_env_int("PORT") == 8080

    def test_raises_when_missing(self) -> None:
        with pytest.raises(RuntimeError, match="MISSING"):
            get_env_int("MISSING")

    def test_returns_default_when_missing(self) -> None:
        assert get_env_int("MISSING", 9999) == 9999

    def test_raises_on_non_numeric(self, monkeypatch: object) -> None:
        monkeypatch.setenv("PORT", "abc")  # type: ignore[attr-defined]
        with pytest.raises(ValueError):
            get_env_int("PORT")


class TestGetEnvList:
    def test_returns_list(self, monkeypatch: object) -> None:
        monkeypatch.setenv("IDS", "a,b,c")  # type: ignore[attr-defined]
        assert get_env_list("IDS") == ["a", "b", "c"]

    def test_strips_whitespace(self, monkeypatch: object) -> None:
        monkeypatch.setenv("IDS", " a , b , c ")  # type: ignore[attr-defined]
        assert get_env_list("IDS") == ["a", "b", "c"]

    def test_filters_empty(self, monkeypatch: object) -> None:
        monkeypatch.setenv("IDS", "a,,b,")  # type: ignore[attr-defined]
        assert get_env_list("IDS") == ["a", "b"]

    def test_returns_empty_when_missing(self) -> None:
        assert get_env_list("MISSING") == []

    def test_returns_split_default(self) -> None:
        assert get_env_list("MISSING", default="x,y") == ["x", "y"]

    def test_custom_separator(self, monkeypatch: object) -> None:
        monkeypatch.setenv("IDS", "a|b|c")  # type: ignore[attr-defined]
        assert get_env_list("IDS", separator="|") == ["a", "b", "c"]
