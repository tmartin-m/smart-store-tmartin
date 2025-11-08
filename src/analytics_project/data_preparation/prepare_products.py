"""
src/analytics_project/data_preparation/prepare_products.py

This script reads data from the data/raw folder, cleans the data,
and writes the cleaned version to the data/prepared folder.

Tasks:
- Remove duplicates
- Handle missing values
- Remove outliers
- Ensure consistent formatting
"""

#####################################
# Import Modules at the Top
#####################################

import pathlib
import sys
import pandas as pd

# Ensure project root is in sys.path for local imports (now 2 parents are needed)
sys.path.append(str(pathlib.Path(__file__).resolve().parent.parent))

from analytics_project.utils.logger import logger
from analytics_project.utils.data_scrubber import DataScrubber

# Constants
SCRIPTS_DATA_PREP_DIR = pathlib.Path(__file__).resolve().parent
SCRIPTS_DIR = SCRIPTS_DATA_PREP_DIR.parent
PROJECT_ROOT = SCRIPTS_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PREPARED_DATA_DIR = DATA_DIR / "prepared"

DATA_DIR.mkdir(exist_ok=True)
RAW_DATA_DIR.mkdir(exist_ok=True)
PREPARED_DATA_DIR.mkdir(exist_ok=True)

#####################################
# Define Functions
#####################################


def read_raw_data(file_name: str) -> pd.DataFrame:
    logger.info(f"FUNCTION START: read_raw_data with file_name={file_name}")
    file_path = RAW_DATA_DIR.joinpath(file_name)
    logger.info(f"Reading data from {file_path}")
    try:
        df = pd.read_csv(file_path)
        logger.info(f"Loaded dataframe with {len(df)} rows and {len(df.columns)} columns")
        profile_data(df)
        return df
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Error reading {file_path}: {e}")
        return pd.DataFrame()


def profile_data(df: pd.DataFrame) -> None:
    logger.info(f"Column datatypes:\n{df.dtypes}")
    logger.info(f"Number of unique values per column:\n{df.nunique()}")


def save_prepared_data(df: pd.DataFrame, file_name: str) -> None:
    logger.info(
        f"FUNCTION START: save_prepared_data with file_name={file_name}, dataframe shape={df.shape}"
    )
    file_path = PREPARED_DATA_DIR.joinpath(file_name)
    df.to_csv(file_path, index=False)
    logger.info(f"Data saved to {file_path}")


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    logger.info(f"FUNCTION START: remove_duplicates with dataframe shape={df.shape}")
    initial_count = len(df)
    # Use ProductID as unique identifier for products
    df = df.drop_duplicates(subset=['ProductID'])
    removed_count = initial_count - len(df)
    logger.info(f"Removed {removed_count} duplicate rows")
    logger.info(f"{len(df)} records remaining after removing duplicates.")
    return df


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    logger.info(f"FUNCTION START: handle_missing_values with dataframe shape={df.shape}")
    missing_by_col = df.isna().sum()
    logger.info(f"Missing values by column before handling:\n{missing_by_col}")

    # Fill missing ProductName with 'Unknown Product'
    if 'ProductName' in df.columns:
        df['ProductName'] = df['ProductName'].fillna('Unknown Product')

    # Fill missing Category with the most common category (mode)
    if 'Category' in df.columns and df['Category'].isnull().any():
        df['Category'] = df['Category'].fillna(df['Category'].mode()[0])

    # Fill missing UnitPrice with the median price
    if 'UnitPrice' in df.columns:
        df['UnitPrice'] = pd.to_numeric(df['UnitPrice'], errors='coerce')
        if df['UnitPrice'].isnull().any():
            df['UnitPrice'] = df['UnitPrice'].fillna(df['UnitPrice'].median())

    # Drop rows without ProductID (assuming ProductID is the unique product code)
    df = df.dropna(subset=['ProductID'])

    # If you have Stock column, drop rows without Stock
    if 'Stock' in df.columns:
        df = df.dropna(subset=['Stock'])

    # If you have Supplier column, fill missing Supplier with 'Unknown Supplier'
    if 'Supplier' in df.columns:
        df['Supplier'] = df['Supplier'].fillna('Unknown Supplier')

    missing_after = df.isna().sum()
    logger.info(f"Missing values by column after handling:\n{missing_after}")
    logger.info(f"{len(df)} records remaining after handling missing values.")
    return df


def remove_outliers(df: pd.DataFrame) -> pd.DataFrame:
    logger.info(f"FUNCTION START: remove_outliers with dataframe shape={df.shape}")
    initial_count = len(df)
    # Identify numeric columns that might have outliers
    numeric_cols = ['UnitPrice']
    for col in numeric_cols:
        if col in df.columns and df[col].dtype in ['float64', 'int64']:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]
            logger.info(f"Applied outlier removal to {col}: bounds [{lower_bound}, {upper_bound}]")
    removed_count = initial_count - len(df)
    logger.info(f"Removed {removed_count} outlier rows")
    logger.info(f"{len(df)} records remaining after removing outliers.")
    return df


def standardize_formats(df: pd.DataFrame) -> pd.DataFrame:
    logger.info(f"FUNCTION START: standardize_formats with dataframe shape={df.shape}")
    # Title case for product names
    if 'ProductName' in df.columns:
        df['ProductName'] = df['ProductName'].str.title()
    # Lowercase for categories
    if 'Category' in df.columns:
        df['Category'] = df['Category'].str.lower()
    # Round prices to 2 decimal places
    if 'UnitPrice' in df.columns:
        df['UnitPrice'] = pd.to_numeric(df['UnitPrice'], errors='coerce').round(2)
    # Title case for supplier names
    if 'Supplier' in df.columns:
        df['Supplier'] = df['Supplier'].str.title()
    logger.info("Completed standardizing formats")
    return df


def validate_data(df: pd.DataFrame) -> pd.DataFrame:
    logger.info(f"FUNCTION START: validate_data with dataframe shape={df.shape}")
    # Check for negative prices
    if 'UnitPrice' in df.columns:
        invalid_prices = df[df['UnitPrice'] < 0].shape[0]
        logger.info(f"Found {invalid_prices} products with negative prices")
        df = df[df['UnitPrice'] >= 0]
    # Check for missing or empty product names
    if 'ProductName' in df.columns:
        missing_names = df[
            df['ProductName'].isnull() | (df['ProductName'].str.strip() == '')
        ].shape[0]
        logger.info(f"Found {missing_names} products with missing or empty names")
        df = df[df['ProductName'].notnull() & (df['ProductName'].str.strip() != '')]
    # Check for missing categories
    if 'Category' in df.columns:
        missing_categories = df[df['Category'].isnull() | (df['Category'].str.strip() == '')].shape[
            0
        ]
        logger.info(f"Found {missing_categories} products with missing or empty categories")
        df = df[df['Category'].notnull() & (df['Category'].str.strip() != '')]
    # Check for products with zero stock
    if 'Stock' in df.columns:
        zero_stock = df[df['Stock'] == 0]
        logger.info(f"Found {zero_stock.shape[0]} products with zero stock.")
    # Check for missing suppliers
    if 'Supplier' in df.columns:
        missing_suppliers = df[df['Supplier'].isnull() | (df['Supplier'].str.strip() == '')].shape[
            0
        ]
        logger.info(f"Found {missing_suppliers} products with missing or empty suppliers")
        df = df[df['Supplier'].notnull() & (df['Supplier'].str.strip() != '')]
    logger.info("Data validation complete")
    return df


def main() -> None:
    logger.info("==================================")
    logger.info("STARTING prepare_products_data.py")
    logger.info("==================================")
    logger.info(f"Root         : {PROJECT_ROOT}")
    logger.info(f"data/raw     : {RAW_DATA_DIR}")
    logger.info(f"data/prepared: {PREPARED_DATA_DIR}")
    logger.info(f"scripts      : {SCRIPTS_DIR}")

    input_file = "products_data.csv"
    output_file = "products_prepared.csv"

    # Read raw data
    df = read_raw_data(input_file)
    if df.empty:
        logger.error("No data loaded. Exiting script.")
        return

    original_shape = df.shape
    logger.info(f"Initial dataframe columns: {', '.join(df.columns.tolist())}")
    logger.info(f"Initial dataframe shape: {df.shape}")

    # Clean column names
    original_columns = df.columns.tolist()
    df.columns = df.columns.str.strip().str.replace(' ', '_')
    changed_columns = [
        f"{old} -> {new}" for old, new in zip(original_columns, df.columns) if old != new
    ]
    if changed_columns:
        logger.info(f"Cleaned column names: {', '.join(changed_columns)}")

    # Remove duplicates
    df = remove_duplicates(df)
    # Handle missing values
    df = handle_missing_values(df)
    # Remove outliers
    df = remove_outliers(df)
    # Validate data
    df = validate_data(df)
    # Standardize formats
    df = standardize_formats(df)
    # Save prepared data
    save_prepared_data(df, output_file)

    logger.info("==================================")
    logger.info(f"Original shape: {original_shape}")
    logger.info(f"Cleaned shape:  {df.shape}")
    logger.info("==================================")
    logger.info("FINISHED prepare_products_data.py")
    logger.info("==================================")


if __name__ == "__main__":
    main()
