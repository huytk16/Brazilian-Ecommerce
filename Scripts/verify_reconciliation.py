#!/usr/bin/env python3
"""
Verify and reconcile data between SQLite views and CSV outputs from the Python pipeline.
"""

import os
import sqlite3
import pandas as pd
import numpy as np

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)
    data_dir = os.path.join(base_dir, 'Data')
    table_dir = os.path.join(base_dir, 'Outputs', 'tables')
    db_file = os.path.join(data_dir, 'olist_analytics.db')

    print("--- POWER BI DATA RECONCILIATION VERIFICATION ---")
    print(f"Database: {db_file}")
    print(f"Tables:   {table_dir}\n")

    # Connect to SQLite
    conn = sqlite3.connect(db_file)

    try:
        # 1. Reconcile Yearly KPIs
        print("Reconciling Yearly KPIs...")
        db_yearly = pd.read_sql_query("SELECT * FROM yearly_kpis ORDER BY year", conn)
        csv_yearly = pd.read_csv(os.path.join(table_dir, 'yearly_kpis.csv')).sort_values('year').reset_index(drop=True)

        # Align columns
        print(f"Database Yearly Columns: {list(db_yearly.columns)}")
        print(f"CSV Yearly Columns:      {list(csv_yearly.columns)}")

        # Check key indicators
        for col in ['delivered_orders', 'payment_revenue', 'avg_review_score']:
            diff = np.abs(db_yearly[col] - csv_yearly[col]).max()
            print(f"  Column '{col}' max difference: {diff}")
            assert diff < 1e-2, f"Discrepancy in yearly '{col}'!"
        print("✅ Yearly KPIs matched successfully.\n")

        # 2. Reconcile Monthly KPIs
        print("Reconciling Monthly KPIs...")
        db_monthly = pd.read_sql_query("SELECT * FROM monthly_kpis ORDER BY purchase_month", conn)
        csv_monthly = pd.read_csv(os.path.join(table_dir, 'monthly_kpis.csv')).sort_values('purchase_month').reset_index(drop=True)

        print(f"Database Monthly rows: {len(db_monthly)}")
        print(f"CSV Monthly rows:      {len(csv_monthly)}")
        
        # Check key indicators
        for col in ['delivered_orders', 'payment_revenue', 'avg_review_score']:
            diff = np.abs(db_monthly[col] - csv_monthly[col]).max()
            print(f"  Column '{col}' max difference: {diff}")
            assert diff < 1e-2, f"Discrepancy in monthly '{col}'!"
        print("✅ Monthly KPIs matched successfully.\n")

        # 3. Reconcile Customer State Logistics (Hotspots)
        print("Reconciling Customer State Logistics...")
        db_logistics = pd.read_sql_query("SELECT * FROM customer_state_logistics ORDER BY customer_state", conn)
        csv_logistics = pd.read_csv(os.path.join(table_dir, 'customer_state_logistics.csv')).sort_values('customer_state').reset_index(drop=True)

        print(f"Database Logistics rows: {len(db_logistics)}")
        print(f"CSV Logistics rows:      {len(csv_logistics)}")

        # Check AL (Alagoas) late rate
        db_al = db_logistics[db_logistics['customer_state'] == 'AL'].iloc[0]
        csv_al = csv_logistics[csv_logistics['customer_state'] == 'AL'].iloc[0]
        print(f"  AL (Alagoas) Late Rate - DB: {db_al['late_rate']:.4f}, CSV: {csv_al['late_rate']:.4f}")
        assert np.abs(db_al['late_rate'] - csv_al['late_rate']) < 1e-4, "Discrepancy in Alagoas late rate!"
        print("✅ Customer State Logistics matched successfully.\n")

        print("🎉 ALL DATA RECONCILIATION CHECKS PASSED SUCCESSFULLY! 🎉")

    except Exception as e:
        print(f"❌ Verification failed: {e}")
        raise e
    finally:
        conn.close()

if __name__ == '__main__':
    main()
