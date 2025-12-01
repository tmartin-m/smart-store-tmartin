"""Module 6: OLAP Goal Script (uses cubed results).

File: src/analytics_project/olap/goal_sales_performanec_by_store.py

Module: analytics_project.olap.goal_sales_performance_by_store

This script uses our precomputed cubed data set to get the information
we need to answer a specific business goal.

GOAL: Analyze sales data to identify trends and optimize resource allocation.

ACTION: This can help inform decisions about reducing operating hours
or focusing marketing efforts on less profitable stores.

PROCESS:
Group transactions by the store_id.
Sum SaleAmount for each store_id.
Identify the store_id with the lowest total revenue.

This example assumes a cube data set with the following column names (yours will differ).
DayOfWeek,store_id,store_name,region,product_id,sale_amount_sum,sale_amount_mean,transaction_id_count,transaction_ids
Sunday,401,Main Street Center,East,2000,2907.93,969.31,3,"[270, 936, 1378]"
"""

import pathlib

import matplotlib.pyplot as plt
import pandas as pd

from analytics_project.utils_logger import logger

import seaborn as sns

# Global constants for paths and key directories

THIS_DIR: pathlib.Path = pathlib.Path(__file__).resolve().parent
DW_DIR: pathlib.Path = THIS_DIR  # src/analytics_project/olap/
PACKAGE_DIR: pathlib.Path = DW_DIR.parent  # src/analytics_project/
SRC_DIR: pathlib.Path = PACKAGE_DIR.parent  # src/
PROJECT_ROOT_DIR: pathlib.Path = SRC_DIR.parent  # project_root/

# Data directories
DATA_DIR: pathlib.Path = PROJECT_ROOT_DIR / "data"
WAREHOUSE_DIR: pathlib.Path = DATA_DIR / "warehouse"

# Warehouse database location (SQLite)
DB_PATH: pathlib.Path = WAREHOUSE_DIR / "smart_sales.db"

# OLAP output directory
OLAP_OUTPUT_DIR: pathlib.Path = DATA_DIR / "olap_cubing_outputs"

# CUBED File path
CUBED_FILE: pathlib.Path = OLAP_OUTPUT_DIR / "multidimensional_olap_cube_by_store.csv"

# Results output directory
RESULTS_OUTPUT_DIR: pathlib.Path = DATA_DIR / "results"

# Recommended - log paths and key directories for debugging

logger.info(f"THIS_DIR:            {THIS_DIR}")
logger.info(f"DW_DIR:              {DW_DIR}")
logger.info(f"PACKAGE_DIR:         {PACKAGE_DIR}")
logger.info(f"SRC_DIR:             {SRC_DIR}")
logger.info(f"PROJECT_ROOT_DIR:    {PROJECT_ROOT_DIR}")

logger.info(f"DATA_DIR:            {DATA_DIR}")
logger.info(f"WAREHOUSE_DIR:       {WAREHOUSE_DIR}")
logger.info(f"DB_PATH:             {DB_PATH}")
logger.info(f"OLAP_OUTPUT_DIR:     {OLAP_OUTPUT_DIR}")
logger.info(f"RESULTS_OUTPUT_DIR:  {RESULTS_OUTPUT_DIR}")

# Create output directory if it does not exist
OLAP_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Create output directory for results if it doesn't exist
RESULTS_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_olap_cube(file_path: pathlib.Path) -> pd.DataFrame:
    """Load the precomputed OLAP cube data."""
    try:
        cube_df = pd.read_csv(file_path)
        logger.info(f"OLAP cube data successfully loaded from {file_path}.")
        return cube_df
    except Exception as e:
        logger.error(f"Error loading OLAP cube data: {e}")
        raise


def analyze_sales_by_store(cube_df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate total sales by store_id."""
    try:
        # Group by store_id and sum the sales
        sales_by_store = cube_df.groupby("store_id")["sale_amount_sum"].sum().reset_index()
        sales_by_store.rename(columns={"sale_amount_sum": "TotalSales"}, inplace=True)
        sales_by_store.sort_values(by="TotalSales", inplace=True)
        logger.info("Sales aggregated by store_id successfully.")
        return sales_by_store
    except Exception as e:
        logger.error(f"Error analyzing sales by store_id: {e}")
        raise


def identify_least_profitable_store(sales_by_store: pd.DataFrame) -> str:
    """Identify the store with the lowest total sales revenue."""
    try:
        least_profitable_store = sales_by_store.iloc[0]
        logger.info(
            f"Least profitable store: {least_profitable_store['store_id']} with revenue ${least_profitable_store['TotalSales']:.2f}."
        )
        return least_profitable_store["store_id"]
    except Exception as e:
        logger.error(f"Error identifying least profitable store: {e}")
        raise


def visualize_sales_by_store(sales_by_store: pd.DataFrame) -> None:
    """Visualize total sales by the store_id."""
    try:
        plt.figure(figsize=(10, 6))
        plt.bar(
            sales_by_store["store_id"],
            sales_by_store["TotalSales"],
            color="skyblue",
        )
        plt.title("Total Sales by Store ID", fontsize=16)
        plt.xlabel("Store ID", fontsize=12)
        plt.ylabel("Total Sales (USD)", fontsize=12)
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Save the visualization
        output_path = RESULTS_OUTPUT_DIR.joinpath("sales_by_store_id.png")
        plt.savefig(output_path)
        logger.info(f"Visualization saved to {output_path}.")
        plt.show()
    except Exception as e:
        logger.error(f"Error visualizing sales by store id: {e}")
        raise


def visualize_sales_pie_chart(sales_by_store: pd.DataFrame) -> None:
    """Visualize revenue share by store as a pie chart."""
    try:
        plt.figure(figsize=(8, 8))
        plt.pie(
            sales_by_store["TotalSales"],
            labels=sales_by_store["store_id"],
            autopct="%1.1f%%",
            startangle=140,
            colors=plt.cm.Paired.colors,
        )
        plt.title("Revenue Share by Store", fontsize=16)
        output_path = RESULTS_OUTPUT_DIR.joinpath("sales_by_store_pie_chart.png")
        plt.savefig(output_path)
        logger.info(f"Pie chart saved to {output_path}.")
        plt.show()
    except Exception as e:
        logger.error(f"Error creating pie chart: {e}")
        raise


def visualize_sales_heatmap(cube_df: pd.DataFrame) -> None:
    """Visualize sales by store and day of week as a heatmap."""
    try:
        # Pivot the cube for heatmap
        pivot_df = cube_df.pivot_table(
            values="sale_amount_sum",
            index="store_id",  # or store_name for readability
            columns="DayOfWeek",
            aggfunc="sum",
            fill_value=0,
        )

        plt.figure(figsize=(10, 6))
        sns.heatmap(pivot_df, cmap="Blues", annot=True, fmt=".0f")
        plt.title("Sales Heatmap by Store and Day of Week", fontsize=16)
        plt.xlabel("Day of Week")
        plt.ylabel("Store ID")
        output_path = RESULTS_OUTPUT_DIR.joinpath("sales_heatmap.png")
        plt.savefig(output_path)
        logger.info(f"Heatmap saved to {output_path}.")
        plt.show()
    except Exception as e:
        logger.error(f"Error creating heatmap: {e}")
        raise


def main():
    logger.info("Starting SALES_LOW_REVENUE_StoreID analysis...")

    # Step 1: Load the precomputed OLAP cube
    cube_df = load_olap_cube(CUBED_FILE)

    # Step 2: Analyze total sales by StoreID
    sales_by_store = analyze_sales_by_store(cube_df)

    # Step 3: Identify the least profitable store
    least_profitable_store = identify_least_profitable_store(sales_by_store)
    logger.info(f"Least profitable store: {least_profitable_store}")

    # Step 4: Visualizations
    visualize_sales_by_store(sales_by_store)  # Existing bar chart
    visualize_sales_pie_chart(sales_by_store)  # ✅ New pie chart
    visualize_sales_heatmap(cube_df)  # ✅ New heatmap

    logger.info("Analysis and visualization completed successfully.")


if __name__ == "__main__":
    main()
