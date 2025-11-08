"""
Module 2: Initial Script to Verify Project Setup.

File: src/analytics_project/data_prep.py
"""

# Imports after the opening docstring
import sys
import pathlib
import pandas as pd

# Ensure src/ is in the Python path
sys.path.append(str(pathlib.Path(__file__).resolve().parent.parent))

from utils_logger import init_logger, logger, project_root
from data_scrubber import DataScrubber

# Set up paths as constants
DATA_DIR: pathlib.Path = project_root.joinpath("data")
RAW_DATA_DIR: pathlib.Path = DATA_DIR.joinpath("raw")
PREPARED_DATA_DIR: pathlib.Path = DATA_DIR.joinpath("prepared")


# Define a reusable function that accepts a full path.
def read_and_log(path: pathlib.Path) -> pd.DataFrame:
    """Read a CSV at the given path into a DataFrame, with friendly logging."""
    try:
        logger.info(f"Reading raw data from {path}.")
        df = pd.read_csv(path)
        logger.info(
            f"{path.name}: loaded DataFrame with shape {df.shape[0]} rows x {df.shape[1]} cols"
        )
        return df
    except FileNotFoundError:
        logger.error(f"File not found: {path}")
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Error reading {path}: {e}")
        return pd.DataFrame()


# Define a main function to start our data processing pipeline.
def main() -> None:
    """Process raw data."""
    logger.info("Starting data preparation...")

    # Build explicit paths for each file under data/raw
    customer_path = RAW_DATA_DIR.joinpath("customers_data.csv")
    product_path = RAW_DATA_DIR.joinpath("products_data.csv")
    sales_path = RAW_DATA_DIR.joinpath("sales_data.csv")

    # === Customers Data ===
    df_customers = read_and_log(customer_path)
    if not df_customers.empty:
        scrubber = DataScrubber(df_customers)
        scrubber.remove_duplicate_records()
        scrubber.handle_missing_data(fill_value="N/A")
        scrubber.format_column_strings_to_lower_and_trim("Name")  # adjust column name if needed
        df_customers_cleaned = scrubber.df
        logger.info("Customer data cleaned.")
        print("Cleaned Customers Data:")
        print(df_customers_cleaned.head())

    # === Products Data ===
    df_products = read_and_log(product_path)
    if not df_products.empty:
        scrubber = DataScrubber(df_products)
        scrubber.remove_duplicate_records()
        scrubber.handle_missing_data(fill_value="Unknown")
        scrubber.format_column_strings_to_upper_and_trim(
            "ProductName"
        )  # adjust column name if needed
        df_products_cleaned = scrubber.df
        logger.info("Product data cleaned.")
        print("Cleaned Products Data:")
        print(df_products_cleaned.head())

    # === Sales Data ===
    df_sales = read_and_log(sales_path)
    if not df_sales.empty:
        scrubber = DataScrubber(df_sales)
        scrubber.remove_duplicate_records()
        scrubber.handle_missing_data(fill_value=0)
        scrubber.parse_dates_to_add_standard_datetime("SaleDate")  # adjust column name if needed
        df_sales_cleaned = scrubber.df
        logger.info("Sales data cleaned.")
        print("Cleaned Sales Data:")
        print(df_sales_cleaned.head())

    logger.info("Data preparation complete.")


# Standard Python idiom to run this module as a script when executed directly.
if __name__ == "__main__":
    init_logger()
    main()
