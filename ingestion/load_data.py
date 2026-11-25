
import os
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, URL, text

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"

url = URL.create(
    "postgresql+psycopg2",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT")),
    database=os.getenv("DB_NAME"),
)

engine = create_engine(url)

datasets = {
    "orders": {
        "file": "orders.csv",
        "dates": ["order_date"],
    },
    "inventory": {
        "file": "inventory.csv",
        "dates": [],
    },
    "shipments": {
        "file": "shipments.csv",
        "dates": [
            "shipped_date",
            "expected_delivery_date",
            "actual_delivery_date",
        ],
    },
}

try:
    with engine.begin() as connection:

        connection.execute(text("SET ROLE seafood_app"))
        logger_placeholder = None

        connection.execute(text("""
            TRUNCATE TABLE
                source.shipments,
                source.inventory,
                source.orders
        """))

        print("Existing source data cleared successfully.")

        for table, config in datasets.items():
            file_path = RAW_DIR / config["file"]

            df = pd.read_csv(
                file_path,
                parse_dates=config["dates"]
            )

            # Convert pandas missing values to SQL NULL
            df = df.astype(object).where(pd.notna(df), None)

            df.to_sql(
                name=table,
                con=connection,
                schema="source",
                if_exists="append",
                index=False,
                chunksize=1000,
                method="multi",
            )

            print(f"Loaded {len(df):,} records into source.{table}")

    print("\nETL ingestion completed successfully!")

except Exception as error:
    print("\nETL ingestion failed:", error)
    raise

finally:
    engine.dispose()
