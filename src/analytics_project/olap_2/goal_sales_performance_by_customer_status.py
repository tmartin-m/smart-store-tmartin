"""
Module 7: OLAP Goal Script (uses cubed results).

File: src/analytics_project/olap_2/goal_sales_performance_by_customer_status.py

Module: analytics_project.olap_2.goal_sales_performance_by_customer_status

GOAL: Analyze sales data to identify trends and optimize resource allocation.
"""

import pathlib
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
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
CUBED_FILE: pathlib.Path = OLAP_OUTPUT_DIR / "multidimensional_olap_cube_by_customer.csv"
RESULTS_OUTPUT_DIR: pathlib.Path = DATA_DIR / "results"

# Create directories if they don't exist
OLAP_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Log paths for debugging
logger.info(f"THIS_DIR:            {THIS_DIR}")
logger.info(f"DATA_DIR:            {DATA_DIR}")
logger.info(f"OLAP_OUTPUT_DIR:     {OLAP_OUTPUT_DIR}")
logger.info(f"RESULTS_OUTPUT_DIR:  {RESULTS_OUTPUT_DIR}")


# -------------------------------
# Functions
# -------------------------------


def load_olap_cube_2(file_path: pathlib.Path) -> pd.DataFrame:
    """Load the precomputed OLAP cube data."""
    try:
        cube_df = pd.read_csv(file_path)
        logger.info(f"OLAP cube data successfully loaded from {file_path}.")
        return cube_df
    except Exception as e:
        logger.error(f"Error loading OLAP cube data: {e}")
        raise


def analyze_sales_by_customer_status(cube_df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate total sales by status."""
    try:
        sales_by_customer_status = cube_df.groupby("status")["sale_amount_sum"].sum().reset_index()
        sales_by_customer_status.rename(columns={"sale_amount_sum": "TotalSales"}, inplace=True)
        sales_by_customer_status.sort_values(by="TotalSales", inplace=True)
        logger.info("Sales aggregated by status successfully.")
        return sales_by_customer_status
    except Exception as e:
        logger.error(f"Error analyzing sales by status: {e}")
        raise


def identify_least_profitable_customer_status(sales_by_customer_status: pd.DataFrame) -> str:
    """Identify the status with the lowest total sales revenue."""
    try:
        least_profitable_customer_status = sales_by_customer_status.iloc[0]
        logger.info(
            f"Least profitable customer status: {least_profitable_customer_status['status']} "
            f"with revenue ${least_profitable_customer_status['TotalSales']:.2f}."
        )
        return least_profitable_customer_status["status"]
    except Exception as e:
        logger.error(f"Error identifying least profitable customer status: {e}")
        raise


def visualize_sales_by_customer_status(sales_by_customer_status: pd.DataFrame) -> None:
    """Visualize total sales by the customer status."""
    try:
        plt.figure(figsize=(10, 6))
        plt.bar(
            sales_by_customer_status["status"],
            sales_by_customer_status["TotalSales"],
            color="skyblue",
        )
        plt.title("Total Sales by Customer Status", fontsize=16)
        plt.xlabel("Status", fontsize=12)
        plt.ylabel("Total Sales (USD)", fontsize=12)
        plt.xticks(rotation=45)
        plt.tight_layout()
        output_path = RESULTS_OUTPUT_DIR.joinpath("sales_by_customer_status.png")
        plt.savefig(output_path)
        logger.info(f"Visualization saved to {output_path}.")
        plt.show()
    except Exception as e:
        logger.error(f"Error visualizing sales by customer status: {e}")
        raise


def visualize_sales_pie_chart(sales_by_customer_status: pd.DataFrame) -> None:
    """Visualize revenue share by customer status as a pie chart."""
    try:
        plt.figure(figsize=(8, 8))
        plt.pie(
            sales_by_customer_status["TotalSales"],
            labels=sales_by_customer_status["status"],
            autopct="%1.1f%%",
            startangle=140,
            colors=plt.cm.Paired.colors,
        )
        plt.title("Revenue Share by Customer Status", fontsize=16)
        output_path = RESULTS_OUTPUT_DIR.joinpath("sales_by_status_pie_chart.png")
        plt.savefig(output_path)
        logger.info(f"Pie chart saved to {output_path}.")
        plt.show()
    except Exception as e:
        logger.error(f"Error creating pie chart: {e}")
        raise


def visualize_sales_heatmap(cube_df: pd.DataFrame) -> None:
    """Heatmap: Sales by store and customer status (no filtering)."""
    try:
        pivot_df = cube_df.pivot_table(
            values="sale_amount_sum",
            index="status",
            columns="store_id",
            aggfunc="sum",
            fill_value=0,
        )
        plt.figure(figsize=(12, 6))
        sns.heatmap(pivot_df, cmap="Blues", annot=True, fmt=".0f")
        plt.title("Sales Heatmap by Store and Customer Status", fontsize=16)
        plt.xlabel("Store ID")
        plt.ylabel("Customer Status")
        output_path = RESULTS_OUTPUT_DIR.joinpath("sales_status_heatmap.png")
        plt.savefig(output_path)
        logger.info(f"Heatmap saved to {output_path}.")
        plt.show()
    except Exception as e:
        logger.error(f"Error creating heatmap: {e}")
        raise


def visualize_sales_heatmap_by_status_and_day(cube_df: pd.DataFrame) -> None:
    """Heatmap: Sales by customer status and day of week."""
    try:
        # Pivot for heatmap (Status vs DayOfWeek)
        pivot_df = cube_df.pivot_table(
            values="sale_amount_sum",
            index="status",
            columns="DayOfWeek",  # Ensure this column exists in your OLAP cube
            aggfunc="sum",
            fill_value=0,
        )

        # Sort columns by weekday order if needed
        weekday_order = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        pivot_df = pivot_df.reindex(
            columns=[day for day in weekday_order if day in pivot_df.columns]
        )

        # Plot heatmap
        plt.figure(figsize=(12, 6))
        sns.heatmap(pivot_df, cmap="Blues", annot=True, fmt=".0f")
        plt.title("Sales Heatmap by Customer Status and Day of Week", fontsize=16)
        plt.xlabel("Day of Week")
        plt.ylabel("Customer Status")

        # Save the visualization
        output_path = RESULTS_OUTPUT_DIR.joinpath("sales_status_day_heatmap.png")
        plt.savefig(output_path)
        logger.info(f"Heatmap saved to {output_path}.")
        plt.show()
    except Exception as e:
        logger.error(f"Error creating heatmap by status and day: {e}")
        raise


def visualize_sales_by_store_and_customer_status(cube_df: pd.DataFrame) -> None:
    """Visualize total sales grouped by store_id and status."""
    try:
        sales_store_customer_status = (
            cube_df.groupby(["store_id", "status"])["sale_amount_sum"].sum().reset_index()
        )
        pivot_df = sales_store_customer_status.pivot(
            index="store_id", columns="status", values="sale_amount_sum"
        ).fillna(0)
        pivot_df.plot(kind="bar", figsize=(12, 6))
        plt.title("Total Sales by Store and Status", fontsize=16)
        plt.xlabel("Store ID", fontsize=12)
        plt.ylabel("Total Sales (USD)", fontsize=12)
        plt.xticks(rotation=45)
        plt.legend(title="Status")
        plt.tight_layout()
        output_path = RESULTS_OUTPUT_DIR.joinpath("sales_by_store_and_customer_status.png")
        plt.savefig(output_path)
        logger.info(f"Store vs Status sales chart saved to {output_path}.")
        plt.show()
    except Exception as e:
        logger.error(f"Error creating store vs status sales visualization: {e}")
        raise


def visualize_sales_by_status_for_all_stores(cube_df: pd.DataFrame) -> None:
    """Generate bar charts comparing total sales for each customer status in every store."""
    try:
        store_ids = cube_df["store_id"].unique()
        for store_id in store_ids:
            store_data = cube_df[cube_df["store_id"] == store_id]
            customer_sales = store_data.groupby("status")["sale_amount_sum"].sum().reset_index()
            customer_sales.sort_values(by="sale_amount_sum", ascending=False, inplace=True)
            plt.figure(figsize=(10, 6))
            plt.bar(
                customer_sales["status"].astype(str),
                customer_sales["sale_amount_sum"],
                color="blue",
            )
            plt.title(f"Total Sales by Customer Status for Store {store_id}", fontsize=16)
            plt.xlabel("Status", fontsize=12)
            plt.ylabel("Total Sales (USD)", fontsize=12)
            plt.xticks(rotation=45)
            plt.tight_layout()
            output_path = RESULTS_OUTPUT_DIR.joinpath(f"status_sales_store_{store_id}.png")
            plt.savefig(output_path)
            logger.info(f"Status sales chart for store {store_id} saved to {output_path}.")
            plt.close()
        logger.info(f"Charts generated for all {len(store_ids)} stores.")
    except Exception as e:
        logger.error(f"Error generating charts for all stores: {e}")
        raise


# -------------------------------
# Main Process
# -------------------------------


def main():
    logger.info("Starting SALES_LOW_REVENUE_Status analysis...")
    cube_df = load_olap_cube_2(CUBED_FILE)
    sales_by_customer_status = analyze_sales_by_customer_status(cube_df)
    least_profitable_customer_status = identify_least_profitable_customer_status(
        sales_by_customer_status
    )
    logger.info(f"Least profitable customer status: {least_profitable_customer_status}")
    visualize_sales_by_customer_status(sales_by_customer_status)
    visualize_sales_pie_chart(sales_by_customer_status)
    visualize_sales_heatmap(cube_df)
    visualize_sales_heatmap_by_status_and_day(cube_df)
    visualize_sales_by_store_and_customer_status(cube_df)
    visualize_sales_by_status_for_all_stores(cube_df)
    logger.info("Analysis and visualization completed successfully.")


if __name__ == "__main__":
    main()
