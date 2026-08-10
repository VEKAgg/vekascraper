from unittest.mock import MagicMock

import pytest
from export_api.config import APIConfig
from export_api.dependencies import get_config_from_app, verify_api_key
from fastapi import HTTPException


def test_verify_api_key_valid() -> None:
    config = APIConfig(api_key="correct-key")
    verify_api_key(config=config, x_api_key="correct-key")


def test_verify_api_key_missing_header() -> None:
    config = APIConfig(api_key="correct-key")
    with pytest.raises(HTTPException) as exc_info:
        verify_api_key(config=config, x_api_key=None)
    assert exc_info.value.status_code == 401


def test_verify_api_key_wrong_key() -> None:
    config = APIConfig(api_key="correct-key")
    with pytest.raises(HTTPException) as exc_info:
        verify_api_key(config=config, x_api_key="wrong-key")
    assert exc_info.value.status_code == 401


def test_get_config_from_app() -> None:
    request = MagicMock()
    config = APIConfig(api_key="test")
    request.app.state.config = config
    assert get_config_from_app(request) is config
