"""
Module 6: OLAP and Cubing Script (Updated for Store Analysis)

File: src/analytics_project/olap/cubing.py
Module: analytics_project.olap.cubing

Purpose:
Create an OLAP cube that aggregates sales data across multiple dimensions,
including store-level analysis.

New Feature:
Added `store_id` (and optionally `store_name`, `region`) to dimensions
for analyzing sales by store.

"""

import pathlib
import sqlite3
import pandas as pd
from analytics_project.utils_logger import logger

# -------------------------------
# Global constants for paths
# -------------------------------
THIS_DIR: pathlib.Path = pathlib.Path(__file__).resolve().parent
DW_DIR: pathlib.Path = THIS_DIR
PACKAGE_DIR: pathlib.Path = DW_DIR.parent
SRC_DIR: pathlib.Path = PACKAGE_DIR.parent
PROJECT_ROOT_DIR: pathlib.Path = SRC_DIR.parent

DATA_DIR: pathlib.Path = PROJECT_ROOT_DIR / "data"
WAREHOUSE_DIR: pathlib.Path = DATA_DIR / "warehouse"
DB_PATH: pathlib.Path = WAREHOUSE_DIR / "smart_sales.db"
OLAP_OUTPUT_DIR: pathlib.Path = DATA_DIR / "olap_cubing_outputs"

# Create output directory if it does not exist
OLAP_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Log paths for debugging
logger.info(f"THIS_DIR:            {THIS_DIR}")
logger.info(f"DW_DIR:              {DW_DIR}")
logger.info(f"PACKAGE_DIR:         {PACKAGE_DIR}")
logger.info(f"SRC_DIR:             {SRC_DIR}")
logger.info(f"PROJECT_ROOT_DIR:    {PROJECT_ROOT_DIR}")
logger.info(f"DATA_DIR:            {DATA_DIR}")
logger.info(f"WAREHOUSE_DIR:       {WAREHOUSE_DIR}")
logger.info(f"DB_PATH:             {DB_PATH}")
logger.info(f"OLAP_OUTPUT_DIR:     {OLAP_OUTPUT_DIR}")


# -------------------------------
# Functions
# -------------------------------


def ingest_sales_data_from_dw() -> pd.DataFrame:
    """Ingest sales data from SQLite data warehouse."""
    try:
        conn = sqlite3.connect(DB_PATH)
        sales_df = pd.read_sql_query("SELECT * FROM sale", conn)
        conn.close()
        logger.info("Sales data successfully loaded from SQLite data warehouse.")
        return sales_df
    except Exception as e:
        logger.error(f"Error loading sale table data from data warehouse: {e}")
        raise


def ingest_store_data_from_dw() -> pd.DataFrame:
    """Ingest store dimension data from SQLite data warehouse."""
    try:
        conn = sqlite3.connect(DB_PATH)
        store_df = pd.read_sql_query("SELECT * FROM store", conn)
        conn.close()
        logger.info("Store data successfully loaded from SQLite data warehouse.")
        return store_df
    except Exception as e:
        logger.error(f"Error loading store table data from data warehouse: {e}")
        raise


def create_olap_cube(sales_df: pd.DataFrame, dimensions: list, metrics: dict) -> pd.DataFrame:
    """Create an OLAP cube by aggregating data across multiple dimensions."""
    try:
        grouped = sales_df.groupby(dimensions)
        cube = grouped.agg(metrics).reset_index()
        cube["transaction_ids"] = grouped["transaction_id"].apply(list).reset_index(drop=True)

        explicit_columns = generate_column_names(dimensions, metrics)
        explicit_columns.append("transaction_ids")
        cube.columns = explicit_columns

        logger.info(f"OLAP cube created with dimensions: {dimensions}")
        return cube
    except Exception as e:
        logger.error(f"Error creating OLAP cube: {e}")
        raise


def generate_column_names(dimensions: list, metrics: dict) -> list:
    """Generate explicit column names for OLAP cube."""
    column_names = dimensions.copy()
    for column, agg_funcs in metrics.items():
        if isinstance(agg_funcs, list):
            for func in agg_funcs:
                column_names.append(f"{column}_{func}")
        else:
            column_names.append(f"{column}_{agg_funcs}")
    column_names = [col.rstrip("_") for col in column_names]
    logger.info(f"Generated column names for OLAP cube: {column_names}")
    return column_names


def write_cube_to_csv(cube: pd.DataFrame, filename: str) -> None:
    """Write the OLAP cube to a CSV file."""
    try:
        output_path = OLAP_OUTPUT_DIR.joinpath(filename)
        cube.to_csv(output_path, index=False)
        logger.info(f"OLAP cube saved to {output_path}.")
    except Exception as e:
        logger.error(f"Error saving OLAP cube to CSV file: {e}")
        raise


# -------------------------------
# Main Process
# -------------------------------


def main():
    logger.info("Starting OLAP Cubing process...")

    # Step 1: Ingest sales data
    sales_df = ingest_sales_data_from_dw()
    if sales_df.empty:
        logger.warning("WARNING: The sales table is empty. Fix ETL process before running cubing.")

    # Step 2: Ingest store data and merge
    store_df = ingest_store_data_from_dw()
    sales_df = sales_df.merge(store_df, on="store_id", how="left")

    # Step 3: Convert sale_date to datetime safely
    sales_df["sale_date"] = pd.to_datetime(sales_df["sale_date"], errors="coerce")
    if sales_df["sale_date"].isna().any():
        invalid_count = sales_df["sale_date"].isna().sum()
        logger.warning(f"{invalid_count} sale_date values could not be parsed and were set to NaT.")
        # Drop rows with invalid dates to avoid issues in OLAP cube
        sales_df = sales_df.dropna(subset=["sale_date"])
        logger.info(f"Rows with invalid dates removed. Remaining rows: {len(sales_df)}")

    # Step 4: Add time-based dimensions
    sales_df["DayOfWeek"] = sales_df["sale_date"].dt.day_name()
    sales_df["Month"] = sales_df["sale_date"].dt.month
    sales_df["Year"] = sales_df["sale_date"].dt.year

    # Step 5: Define dimensions and metrics (include store info)
    dimensions = ["DayOfWeek", "store_id", "store_name", "region", "product_id"]
    metrics = {"sale_amount": ["sum", "mean"], "transaction_id": "count"}

    # Step 6: Create the cube
    olap_cube = create_olap_cube(sales_df, dimensions, metrics)

    # Step 7: Save the cube
    write_cube_to_csv(olap_cube, "multidimensional_olap_cube_by_store.csv")

    logger.info("OLAP Cubing process completed successfully.")
    logger.info(f"Please see outputs in {OLAP_OUTPUT_DIR}")


if __name__ == "__main__":
    main()
