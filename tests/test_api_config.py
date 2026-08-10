from export_api.config import APIConfig


def test_repr_masks_api_key() -> None:
    cfg = APIConfig(api_key="secret123456")
    assert "secr***" in repr(cfg)


def test_repr_shows_not_set_when_empty() -> None:
    cfg = APIConfig(api_key="")
    assert "NOT SET" in repr(cfg)


def test_repr_includes_host_and_port() -> None:
    cfg = APIConfig(api_key="key", host="1.2.3.4", port=9000)
    r = repr(cfg)
    assert "1.2.3.4" in r
    assert "9000" in r
