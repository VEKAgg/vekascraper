import sys

from member_worker.config import WorkerConfig
from member_worker.worker import run_worker

if __name__ == "__main__":
    config = WorkerConfig.from_env()
    run_worker(config)
    sys.exit(0)
