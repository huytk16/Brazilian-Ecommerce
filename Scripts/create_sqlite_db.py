#!/usr/bin/env python3
"""
Create SQLite Database for Olist Brazilian E-Commerce Analytics.
This script:
1. Loads 9 Olist CSV datasets from the Data directory into a SQLite database.
2. Creates core analysis views from SQL/01_olist_core_analysis.sql.
3. Runs validation queries to ensure views are set up correctly.
"""

import os
import sqlite3
import pandas as pd

def main():
    # Setup paths relative to the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)
    data_dir = os.path.join(base_dir, 'Data')
    sql_file = os.path.join(base_dir, 'SQL', '01_olist_core_analysis.sql')
    db_file = os.path.join(data_dir, 'olist_analytics.db')

    print(f"Base Directory: {base_dir}")
    print(f"Data Directory: {data_dir}")
    print(f"Database Path:  {db_file}")
    print(f"SQL Script:     {sql_file}\n")

    # CSV mapping to SQLite tables
    csv_to_table = {
        'olist_customers_dataset.csv': 'customers',
        'olist_geolocation_dataset.csv': 'geolocation',
        'olist_order_items_dataset.csv': 'items',
        'olist_order_payments_dataset.csv': 'payments',
        'olist_order_reviews_dataset.csv': 'reviews',
        'olist_orders_dataset.csv': 'orders',
        'olist_products_dataset.csv': 'products',
        'olist_sellers_dataset.csv': 'sellers',
        'product_category_name_translation.csv': 'translation'
    }

    # Ensure Data directory exists
    os.makedirs(data_dir, exist_ok=True)

    # Connect to SQLite
    print("Connecting to SQLite database...")
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    try:
        # 1. Load CSVs into SQLite
        for csv_filename, table_name in csv_to_table.items():
            csv_path = os.path.join(data_dir, csv_filename)
            if not os.path.exists(csv_path):
                raise FileNotFoundError(f"Required CSV not found: {csv_path}")

            print(f"Loading {csv_filename} into table '{table_name}'...")
            # Using pandas to load CSV
            df = pd.read_csv(csv_path)
            
            # Write to SQLite
            df.to_sql(table_name, conn, if_exists='replace', index=False)
            print(f"  -> Loaded {len(df):,} rows.")

        # 2. Execute SQL View script
        if not os.path.exists(sql_file):
            raise FileNotFoundError(f"SQL views definition script not found: {sql_file}")

        print(f"\nExecuting view definitions from {os.path.basename(sql_file)}...")
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_script = f.read()

        # Executescript executes multiple SQL statements separated by semicolons
        cursor.executescript(sql_script)
        conn.commit()
        print("Views created successfully.")

        # 3. Verify views by running queries
        print("\nVerifying views...")
        
        # Query 1: COUNT(*) FROM df_master
        cursor.execute("SELECT COUNT(*) FROM df_master")
        df_master_count = cursor.fetchone()[0]
        print(f"SELECT COUNT(*) FROM df_master: {df_master_count:,}")

        # Query 2: COUNT(*) FROM yearly_kpis
        cursor.execute("SELECT COUNT(*) FROM yearly_kpis")
        yearly_kpis_count = cursor.fetchone()[0]
        print(f"SELECT COUNT(*) FROM yearly_kpis: {yearly_kpis_count:,}")

        # Display content of yearly_kpis
        print("\nYearly KPIs Content:")
        cursor.execute("SELECT * FROM yearly_kpis")
        colnames = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        
        # Format printing header and rows
        header_str = " | ".join(colnames)
        print(header_str)
        print("-" * len(header_str))
        for row in rows:
            print(" | ".join(str(val) for val in row))

    except Exception as e:
        print(f"\nError occurred: {e}")
        conn.rollback()
        raise e
    finally:
        conn.close()
        print("\nDatabase connection closed.")

if __name__ == '__main__':
    main()
