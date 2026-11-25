
import os
import logging
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, URL, text

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "data_quality.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

url = URL.create(
    "postgresql+psycopg2",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT")),
    database=os.getenv("DB_NAME"),
)

engine = create_engine(url)

checks = {
    "Orders record count": """
        SELECT COUNT(*) = 10000 FROM source.orders
    """,
    "Inventory record count": """
        SELECT COUNT(*) = 5000 FROM source.inventory
    """,
    "Shipments record count": """
        SELECT COUNT(*) = 8000 FROM source.shipments
    """,
    "Duplicate order IDs": """
        SELECT COUNT(*) = 0
        FROM (
            SELECT order_id
            FROM source.orders
            GROUP BY order_id
            HAVING COUNT(*) > 1
        ) duplicates
    """,
    "Invalid shipment references": """
        SELECT COUNT(*) = 0
        FROM source.shipments s
        LEFT JOIN source.orders o ON s.order_id = o.order_id
        WHERE o.order_id IS NULL
    """,
    "Invalid order quantities": """
        SELECT COUNT(*) = 0
        FROM source.orders
        WHERE quantity IS NULL OR quantity <= 0
    """,
    "Invalid inventory quantities": """
        SELECT COUNT(*) = 0
        FROM source.inventory
        WHERE quantity_on_hand IS NULL OR quantity_on_hand < 0
    """,
    "Missing customer IDs": """
        SELECT COUNT(*) = 0
        FROM source.orders
        WHERE customer_id IS NULL
    """
}

def run_checks():
    passed = 0
    failed = 0

    try:
        with engine.connect() as connection:
            for check_name, query in checks.items():
                result = connection.execute(text(query)).scalar()

                if result:
                    logger.info("PASS | %s", check_name)
                    passed += 1
                else:
                    logger.error("FAIL | %s", check_name)
                    failed += 1

        logger.info(
            "SUMMARY | Passed: %s | Failed: %s",
            passed, failed
        )

        if failed:
            raise RuntimeError("Data quality checks failed.")

        logger.info("DATA QUALITY VALIDATION SUCCESSFUL")

    except Exception:
        logger.exception("DATA QUALITY VALIDATION ERROR")
        raise

    finally:
        engine.dispose()


if __name__ == "__main__":
    run_checks()
