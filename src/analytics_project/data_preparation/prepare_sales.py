import pathlib
import sys
import pandas as pd

sys.path.append(str(pathlib.Path(__file__).resolve().parent.parent))
from analytics_project.utils.logger import logger
from analytics_project.utils.data_scrubber import DataScrubber

SCRIPTS_DATA_PREP_DIR = pathlib.Path(__file__).resolve().parent
SCRIPTS_DIR = SCRIPTS_DATA_PREP_DIR.parent
PROJECT_ROOT = SCRIPTS_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PREPARED_DATA_DIR = DATA_DIR / "prepared"

DATA_DIR.mkdir(exist_ok=True)
RAW_DATA_DIR.mkdir(exist_ok=True)
PREPARED_DATA_DIR.mkdir(exist_ok=True)


def read_raw_data(file_name: str) -> pd.DataFrame:
    logger.info(f"FUNCTION START: read_raw_data with file_name={file_name}")
    file_path = RAW_DATA_DIR.joinpath(file_name)
    logger.info(f"Reading data from {file_path}")
    df = pd.read_csv(file_path)
    logger.info(f"Loaded dataframe with {len(df)} rows and {len(df.columns)} columns")
    logger.info(f"Column datatypes:\n{df.dtypes}")
    logger.info(f"Number of unique values per column:\n{df.nunique()}")
    return df


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
    for col in ['TransactionID', 'SaleID', 'CustomerID']:
        if col in df.columns:
            df = df.drop_duplicates(subset=[col])
            logger.info(f"Removed duplicates using {col}")
            break
    removed_count = initial_count - len(df)
    logger.info(f"Removed {removed_count} duplicate rows")
    logger.info(f"{len(df)} records remaining after removing duplicates.")
    return df


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    logger.info(f"FUNCTION START: handle_missing_values with dataframe shape={df.shape}")
    missing_by_col = df.isna().sum()
    logger.info(f"Missing values by column before handling:\n{missing_by_col}")

    if 'CustomerID' in df.columns:
        df['CustomerID'] = df['CustomerID'].fillna('Unknown')

    if 'PaymentMethod' in df.columns and df['PaymentMethod'].isnull().any():
        df['PaymentMethod'] = df['PaymentMethod'].fillna(df['PaymentMethod'].mode()[0])

    if 'SaleAmount' in df.columns:
        df['SaleAmount'] = pd.to_numeric(df['SaleAmount'], errors='coerce')
        if df['SaleAmount'].isnull().any():
            df['SaleAmount'] = df['SaleAmount'].fillna(df['SaleAmount'].median())

    if 'DiscountPercentage' in df.columns:
        df['DiscountPercentage'] = pd.to_numeric(df['DiscountPercentage'], errors='coerce')
        df = df.dropna(subset=['DiscountPercentage'])

    if 'CampaignID' in df.columns:
        df['CampaignID'] = df['CampaignID'].fillna('Unknown ID')

    missing_after = df.isna().sum()
    logger.info(f"Missing values by column after handling:\n{missing_after}")
    logger.info(f"{len(df)} records remaining after handling missing values.")
    return df


def remove_outliers(df: pd.DataFrame) -> pd.DataFrame:
    logger.info(f"FUNCTION START: remove_outliers with dataframe shape={df.shape}")
    initial_count = len(df)
    numeric_cols = ['DiscountPercentage', 'SaleAmount']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
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
    if 'PaymentMethod' in df.columns:
        df['PaymentMethod'] = df['PaymentMethod'].str.title()
    if 'SaleAmount' in df.columns:
        df['SaleAmount'] = pd.to_numeric(df['SaleAmount'], errors='coerce').round(2)
    logger.info("Completed standardizing formats")
    return df


def validate_data(df: pd.DataFrame) -> pd.DataFrame:
    logger.info(f"FUNCTION START: validate_data with dataframe shape={df.shape}")
    if 'DiscountPercentage' in df.columns:
        df['DiscountPercentage'] = pd.to_numeric(df['DiscountPercentage'], errors='coerce')
        invalid_discount = df[df['DiscountPercentage'] < 0].shape[0]
        logger.info(f"Found {invalid_discount} records with negative DiscountPercentage")
        df = df[df['DiscountPercentage'] >= 0]
    if 'PaymentMethod' in df.columns:
        missing_methods = df[
            df['PaymentMethod'].isnull() | (df['PaymentMethod'].str.strip() == '')
        ].shape[0]
        logger.info(f"Found {missing_methods} records with missing or empty PaymentMethods")
        df = df[df['PaymentMethod'].notnull() & (df['PaymentMethod'].str.strip() != '')]
    if 'Category' in df.columns:
        missing_categories = df[df['Category'].isnull() | (df['Category'].str.strip() == '')].shape[
            0
        ]
        logger.info(f"Found {missing_categories} records with missing or empty categories")
        df = df[df['Category'].notnull() & (df['Category'].str.strip() != '')]
    logger.info("Data validation complete")
    return df


def main() -> None:
    logger.info("==================================")
    logger.info("STARTING prepare_sales_data.py")
    logger.info("==================================")
    logger.info(f"Root         : {PROJECT_ROOT}")
    logger.info(f"data/raw     : {RAW_DATA_DIR}")
    logger.info(f"data/prepared: {PREPARED_DATA_DIR}")
    logger.info(f"scripts      : {SCRIPTS_DIR}")

    input_file = "sales_data.csv"
    output_file = "sales_prepared.csv"

    df = read_raw_data(input_file)
    if df.empty:
        logger.error("No data loaded. Exiting script.")
        return

    original_shape = df.shape
    logger.info(f"Initial dataframe columns: {', '.join(df.columns.tolist())}")
    logger.info(f"Initial dataframe shape: {df.shape}")

    original_columns = df.columns.tolist()
    df.columns = df.columns.str.strip().str.replace(' ', '_')
    changed_columns = [
        f"{old} -> {new}" for old, new in zip(original_columns, df.columns) if old != new
    ]
    if changed_columns:
        logger.info(f"Cleaned column names: {', '.join(changed_columns)}")

    df = remove_duplicates(df)
    df = handle_missing_values(df)
    df = remove_outliers(df)
    df = validate_data(df)
    df = standardize_formats(df)
    save_prepared_data(df, output_file)

    logger.info("==================================")
    logger.info(f"Original shape: {original_shape}")
    logger.info(f"Cleaned shape:  {df.shape}")
    logger.info("==================================")
    logger.info("FINISHED prepare_sales_data.py")
    logger.info("==================================")


if __name__ == "__main__":
    main()
