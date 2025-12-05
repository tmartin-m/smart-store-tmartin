"""
Module 7: Custom BI Project

File: src/analytics_project/olap_2/cubing_2.py
Module: analytics_project.olap_2.cubing_2

Purpose:
Create an OLAP cube that aggregates sales data across multiple dimensions,
including customer level analysis.
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


def ingest_customer_data_from_dw() -> pd.DataFrame:
    """Ingest customer dimension data from SQLite data warehouse."""
    try:
        conn = sqlite3.connect(DB_PATH)
        customer_df = pd.read_sql_query("SELECT * FROM customer", conn)
        conn.close()
        logger.info("Customer data successfully loaded from SQLite data warehouse.")
        return customer_df
    except Exception as e:
        logger.error(f"Error loading customer table data from data warehouse: {e}")
        raise


def create_olap_cube_2(sales_df: pd.DataFrame, dimensions: list, metrics: dict) -> pd.DataFrame:
    """Create an OLAP cube by aggregating data across multiple dimensions."""
    try:
        # Validate dimensions exist in DataFrame
        missing_dims = [dim for dim in dimensions if dim not in sales_df.columns]
        if missing_dims:
            logger.warning(
                f"Missing dimensions in DataFrame: {missing_dims}. They will be ignored."
            )
            dimensions = [dim for dim in dimensions if dim in sales_df.columns]

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

    # Step 2: Ingest customer data
    customer_df = ingest_customer_data_from_dw()

    # Step 3: Convert join_date to datetime safely
    customer_df["join_date"] = pd.to_datetime(customer_df["join_date"], errors="coerce")
    if customer_df["join_date"].isna().any():
        invalid_count = customer_df["join_date"].isna().sum()
        logger.warning(f"{invalid_count} join_date values could not be parsed and were set to NaT.")
        customer_df = customer_df.dropna(subset=["join_date"])
        logger.info(f"Rows with invalid dates removed. Remaining rows: {len(customer_df)}")

    # Step 4: Add time-based dimensions BEFORE merging
    customer_df["DayOfWeek"] = customer_df["join_date"].dt.day_name()
    customer_df["Month"] = customer_df["join_date"].dt.month
    customer_df["Year"] = customer_df["join_date"].dt.year

    # Step 5: Merge customer info into sales_df
    sales_df = sales_df.merge(customer_df, on="customer_id", how="left")

    # Step 6: Define dimensions (match exact column names)
    dimensions = [
        "DayOfWeek",
        "Month",
        "Year",
        "store_id",
        "product_id",
        "customer_id",
        "status",
        "campaign_id",
        "payment_method",
    ]

    # Step 7: Define metrics (use pandas-friendly names)
    metrics = {
        "sale_amount": ["sum", "mean"],
        "discount_percentage": ["mean", "max", "min"],
        "points": "mean",
    }

    # Step 8: Create the cube
    olap_cube_2 = create_olap_cube_2(sales_df, dimensions, metrics)

    # Step 9: Save the cube
    write_cube_to_csv(olap_cube_2, "multidimensional_olap_cube_by_customer.csv")

    logger.info("OLAP Cubing process completed successfully.")
    logger.info(f"Please see outputs in {OLAP_OUTPUT_DIR}")


if __name__ == "__main__":
    main()
