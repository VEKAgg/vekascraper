import sys

import uvicorn
from export_api.app import create_app
from export_api.config import APIConfig

if __name__ == "__main__":
    config = APIConfig.from_env()
    app = create_app(config)
    uvicorn.run(app, host=config.host, port=config.port, log_level="info")
    sys.exit(0)
