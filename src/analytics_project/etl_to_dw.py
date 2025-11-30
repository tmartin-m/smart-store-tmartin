"""ETL script to load prepared data into the data warehouse (SQLite database).

File: src/analytics_project/etl_to_dw.py

This file assumes the following structure (yours may vary):

project_root/
│
├─ data/
│   ├─ raw/
│   ├─ prepared/
│   └─ warehouse/
│
└─ src/
    └─ analytics_project/
        ├─ data_preparation/
        ├─ dw/
        ├─ analytics/
        └─ utils_logger.py

By switching to a modern src/ layout and using __init__.py files,
we no longer need any sys.path modifications.

Remember to put __init__.py files (empty is fine) in each folder to make them packages.

NOTE on column names: This example uses inconsistent naming conventions for column names in the cleaned data.
A good business intelligence project would standardize these during data preparation.
Your names should be more standard after cleaning and pre-processing the data.

Database names generally follow snake_case conventions for SQL compatibility.
"snake_case" =  all lowercase with underscores between words.
"""

# Imports at the top

import pathlib
import sqlite3

import pandas as pd

from analytics_project.utils_logger import logger

# Global constants for paths and key directories

THIS_DIR: pathlib.Path = pathlib.Path(__file__).resolve().parent
PACKAGE_DIR: pathlib.Path = THIS_DIR  # src/analytics_project/
SRC_DIR: pathlib.Path = PACKAGE_DIR.parent  # src/
PROJECT_ROOT_DIR: pathlib.Path = SRC_DIR.parent  # project_root/

# Data directories
DATA_DIR: pathlib.Path = PROJECT_ROOT_DIR / "data"
RAW_DATA_DIR: pathlib.Path = DATA_DIR / "raw"
CLEAN_DATA_DIR: pathlib.Path = DATA_DIR / "prepared"
WAREHOUSE_DIR: pathlib.Path = DATA_DIR / "warehouse"

# Warehouse database location (SQLite)
DB_PATH: pathlib.Path = WAREHOUSE_DIR / "smart_sales.db"

# Recommended - log paths and key directories for debugging

logger.info(f"THIS_DIR:            {THIS_DIR}")
logger.info(f"PACKAGE_DIR:         {PACKAGE_DIR}")
logger.info(f"SRC_DIR:             {SRC_DIR}")
logger.info(f"PROJECT_ROOT_DIR:    {PROJECT_ROOT_DIR}")

logger.info(f"DATA_DIR:            {DATA_DIR}")
logger.info(f"RAW_DATA_DIR:        {RAW_DATA_DIR}")
logger.info(f"CLEAN_DATA_DIR:      {CLEAN_DATA_DIR}")
logger.info(f"WAREHOUSE_DIR:       {WAREHOUSE_DIR}")
logger.info(f"DB_PATH:             {DB_PATH}")


def create_schema(cursor: sqlite3.Cursor) -> None:
    """Create tables in the data warehouse if they don't exist."""
    cursor.execute("PRAGMA foeign_keys = ON;")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customer (
            customer_id INTEGER PRIMARY KEY,
            name TEXT,
            region TEXT,
            join_date TEXT,
            status TEXT,
            points INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS product (
            product_id INTEGER PRIMARY KEY,
            product_name TEXT,
            category TEXT,
            unit_price REAL,
            stock INTEGER,
            supplier TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS store (
            store_id INTEGER PRIMARY KEY,
            store_name TEXT NOT NULL,
            city TEXT NOT NULL,
            state TEXT NOT NULL,
            location_type TEXT NOT NULL,
            region TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sale (
            transaction_id INTEGER PRIMARY KEY,
            sale_date TEXT,
            customer_id INTEGER,
            product_id INTEGER,
            store_id INTEGER,
            campaign_id INTEGER,
            sale_amount REAL,
            discount_percentage REAL,
            payment_method TEXT,
            FOREIGN KEY (customer_id) REFERENCES customer (customer_id),
            FOREIGN KEY (product_id) REFERENCES product (product_id),
            FOREIGN KEY (store_id) REFERENCES store (store_id)
        )
    """)


def delete_existing_records(cursor: sqlite3.Cursor) -> None:
    """Delete all existing records from the customer, product, store and sale tables."""
    cursor.execute("DELETE FROM customer")
    cursor.execute("DELETE FROM product")
    cursor.execute("DELETE FROM store")
    cursor.execute("DELETE FROM sale")


def insert_customers(customers_df: pd.DataFrame, cursor: sqlite3.Cursor) -> None:
    """Insert customer data into the customer table."""
    logger.info(f"Inserting {len(customers_df)} customer rows.")
    customers_df.to_sql("customer", cursor.connection, if_exists="append", index=False)


def insert_products(products_df: pd.DataFrame, cursor: sqlite3.Cursor) -> None:
    """Insert product data into the product table."""
    logger.info(f"Inserting {len(products_df)} product rows.")
    products_df.to_sql("product", cursor.connection, if_exists="append", index=False)


def insert_stores(stores_df: pd.DataFrame, cursor: sqlite3.Cursor) -> None:
    """Insert store data into the store table."""
    logger.info(f"Inserting {len(stores_df)} store rows.")
    stores_df.to_sql("store", cursor.connection, if_exists="append", index=False)


def insert_sales(sales_df: pd.DataFrame, cursor: sqlite3.Cursor) -> None:
    """Insert sales data into the sales table."""
    logger.info(f"Inserting {len(sales_df)} sale rows.")
    sales_df.to_sql("sale", cursor.connection, if_exists="append", index=False)


def load_data_to_db() -> None:
    """Load clean data into the data warehouse."""
    logger.info("Starting ETL: loading clean data into the warehouse.")

    # Make sure the warehouse directory exists
    WAREHOUSE_DIR.mkdir(parents=True, exist_ok=True)

    # If an old database exists, remove and recreate with the latest table definitions.
    if DB_PATH.exists():
        logger.info(f"Removing existing warehouse database at: {DB_PATH}")
        DB_PATH.unlink()

    # Initialize a connection variable
    # before the try block so we can close it in finally
    conn: sqlite3.Connection | None = None

    try:
        # Connect to SQLite. Create the file if it doesn't exist
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Create schema and clear existing records
        create_schema(cursor)
        delete_existing_records(cursor)

        # Load prepared data using pandas
        customers_df = pd.read_csv(CLEAN_DATA_DIR.joinpath("customers_prepared.csv"))
        products_df = pd.read_csv(CLEAN_DATA_DIR.joinpath("products_prepared.csv"))
        stores_df = pd.read_csv(CLEAN_DATA_DIR.joinpath("stores_prepared.csv"))
        # TODO: Uncomment after implementing sales data preparation
        sales_df = pd.read_csv(CLEAN_DATA_DIR.joinpath("sales_prepared.csv"))

        # Rename clean columns to match database schema if necessary
        # Clean column name : Database column name
        customers_df = customers_df.rename(
            columns={
                "CustomerID": "customer_id",
                "Name": "name",
                "Region": "region",
                "JoinDate": "join_date",
                "Status": "status",
                "Points": "points",
            }
        )
        logger.info(f"Customer columns (cleaned): {list(customers_df.columns)}")

        # Rename clean columns to match database schema if necessary
        # Clean column name : Database column name
        products_df = products_df.rename(
            columns={
                "ProductID": "product_id",
                "ProductName": "product_name",
                "Category": "category",
                "UnitPrice": "unit_price",
                "Stock": "stock",
                "Supplier": "supplier",
            }
        )
        logger.info(f"Product columns (cleaned):  {list(products_df.columns)}")

        # Rename clean columns to match database schema if necessary
        # Clean column name : Database column name
        stores_df = stores_df.rename(
            columns={
                "StoreID": "store_id",
                "StoreName": "store_name",
                "City": "city",
                "State": "state",
                "LocationType": "location_type",
                "Region": "region",
            }
        )
        logger.info(f"Product columns (cleaned):  {list(products_df.columns)}")

        # TODO: Rename sales_df columns to match database schema if necessary

        # Rename clean columns to match database schema if necessary

        # Clean column name : Database column name
        sales_df = sales_df.rename(
            columns={
                "TransactionID": "transaction_id",
                "SaleDate": "sale_date",
                "CustomerID": "customer_id",
                "ProductID": "product_id",
                "StoreID": "store_id",
                "CampaignID": "campaign_id",
                "SaleAmount": "sale_amount",
                "DiscountPercentage": "discount_percentage",
                "PaymentMethod": "payment_method",
            }
        )
        logger.info(f"Sales columns (cleaned):  {list(sales_df.columns)}")

        # Drop duplicates
        for df, name, key in [
            (customers_df, "customers", "customer_id"),
            (products_df, "products", "product_id"),
            (stores_df, "stores", "store_id"),
            (sales_df, "sales", "transaction_id"),
        ]:
            before = len(df)
            df.drop_duplicates(subset=[key], inplace=True)
            after = len(df)
            if before != after:
                logger.warning(f"Dropped {before - after} duplicate rows from {name}.")

        # Insert data into the database for all tables

        insert_customers(customers_df, cursor)

        insert_products(products_df, cursor)

        insert_stores(stores_df, cursor)

        # TODO: Uncomment after implementing sales data preparation
        insert_sales(sales_df, cursor)

        conn.commit()
        logger.info("ETL finished successfully. Data loaded into the warehouse.")
    finally:
        # Regardless of success or failure, close the DB connection if it exists
        if conn is not None:
            logger.info("Closing database connection.")
            conn.close()


if __name__ == "__main__":
    load_data_to_db()
