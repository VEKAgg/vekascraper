import sys

from message_worker.config import WorkerConfig
from message_worker.worker import run_worker

if __name__ == "__main__":
    config = WorkerConfig.from_env()
    run_worker(config)
    sys.exit(0)
