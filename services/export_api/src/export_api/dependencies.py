from __future__ import annotations

import hmac

from export_api.config import APIConfig
from fastapi import Depends, Header, HTTPException, Request, status


def get_config_from_app(request: Request) -> APIConfig:
    return request.app.state.config


def verify_api_key(
    config: APIConfig = Depends(get_config_from_app),
    x_api_key: str | None = Header(None, alias="X-API-Key"),
) -> None:
    if x_api_key is None or not hmac.compare_digest(x_api_key, config.api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
