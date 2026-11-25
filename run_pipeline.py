
import logging
import subprocess
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "pipeline.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

STEPS = [
    ("Data Generation", "ingestion/generate_data.py"),
    ("Data Loading", "ingestion/load_data.py"),
    ("Data Quality Validation", "ingestion/validate_data.py"),
]

def run_pipeline():
    pipeline_start = time.perf_counter()

    logger.info("========== PIPELINE STARTED ==========")

    try:
        for step_name, script_path in STEPS:
            logger.info("STARTED: %s", step_name)
            step_start = time.perf_counter()

            result = subprocess.run(
                [sys.executable, str(BASE_DIR / script_path)],
                cwd=BASE_DIR,
                check=True
            )

            duration = time.perf_counter() - step_start

            logger.info(
                "SUCCESS: %s | Duration: %.2f seconds",
                step_name,
                duration
            )

        total_duration = time.perf_counter() - pipeline_start

        logger.info(
            "========== PIPELINE SUCCESS | Total: %.2f seconds ==========",
            total_duration
        )

    except subprocess.CalledProcessError as error:
        logger.error(
            "PIPELINE FAILED | Script: %s | Exit code: %s",
            error.cmd,
            error.returncode
        )
        raise

    except Exception:
        logger.exception("UNEXPECTED PIPELINE ERROR")
        raise


if __name__ == "__main__":
    run_pipeline()
    