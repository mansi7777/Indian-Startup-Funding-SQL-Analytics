# load_data.py

import pandas as pd
import psycopg2
from psycopg2 import sql
import os

# --- Configuration ---
DB_NAME = "startup_db"
DB_USER = ""
DB_PASS = ""
DB_HOST = "localhost"
CSV_FILE = "data/indian_startups_funding.csv"

def execute_sql_file(conn, file_path):
    """Executes all SQL commands in a file (e.g., schema.sql)."""
    try:
        with open(file_path, 'r') as f:
            sql_script = f.read()
        cursor = conn.cursor()
        cursor.execute(sql_script)
        conn.commit()
        print(f"Successfully executed {file_path}")
    except Exception as e:
        print(f"Error executing {file_path}: {e}")
        conn.rollback()
        raise

def normalize_and_load_data(conn):
    """Reads the single CSV, normalizes data, and loads it into defined tables."""
    print("\n--- Starting Data Normalization and Loading ---")
    
    # 1. READ THE SOURCE DATA
    try:
        df_source = pd.read_csv(CSV_FILE, encoding='latin1')
        df_source.columns = df_source.columns.str.lower().str.replace(' ', '_').str.replace(':', '')
        print(f"Read {len(df_source)} rows from {CSV_FILE}")
    except FileNotFoundError:
        print(f"ERROR: Source file not found at {CSV_FILE}. Check your 'data' folder.")
        return
    except Exception as e:
        print(f"ERROR reading CSV: {e}")
        return

    
    df_source['date'] = pd.to_datetime(df_source['date'], errors='coerce')
    df_source.rename(columns={'amount_in_usd': 'amount_usd', 's_no': 'temp_id'}, inplace=True)
    
  
    cursor = conn.cursor()
    
    # A. INDUSTRIES Table (Unique list of industry names)
    df_industries = df_source[['industry']].dropna().drop_duplicates().reset_index(drop=True)
    df_industries['industry_id'] = df_industries.index + 1
    load_table(cursor, conn, df_industries, 'industries')

    # B. INVESTORS Table (Unique list of investors)
    df_investors = (df_source['investors'].str.split(',', expand=True).stack().str.strip()
                    .dropna().drop_duplicates().reset_index(drop=True).to_frame(name='name'))
    df_investors['investor_id'] = df_investors.index + 1
    load_table(cursor, conn, df_investors, 'investors')

    # C. STARTUPS Table (Need to map foreign keys)
    df_startups = df_source[['startup_name', 'city', 'industry']].drop_duplicates().dropna(subset=['startup_name'])
    df_startups = df_startups.merge(df_industries, on='industry', how='left')
    df_startups.rename(columns={'startup_name': 'name'}, inplace=True)
    df_startups.drop(columns=['industry'], inplace=True)
    df_startups['startup_id'] = df_startups.reset_index().index + 1
    load_table(cursor, conn, df_startups[['startup_id', 'name', 'city', 'industry_id']], 'startups')

    # D. FUNDING_ROUNDS Table
    df_funding = df_source[['startup_name', 'date', 'round_type', 'amount_usd']].dropna(subset=['startup_name', 'date', 'amount_usd', 'round_type'])
    df_funding = df_funding.merge(df_startups[['name', 'startup_id']], left_on='startup_name', right_on='name', how='left')
    df_funding.rename(columns={'round_type': 'round_type', 'amount_usd': 'amount_usd'}, inplace=True)
    df_funding.drop(columns=['startup_name', 'name'], inplace=True)
    df_funding['round_id'] = df_funding.reset_index().index + 1
    load_table(cursor, conn, df_funding[['round_id', 'startup_id', 'date', 'round_type', 'amount_usd']], 'funding_rounds')
    
    # E. ROUND_INVESTORS Table (The linking/junction table)
    investor_rounds = []
    round_id_map = df_funding.set_index('startup_id')['round_id'].to_dict()
    startup_id_map = df_startups.set_index('name')['startup_id'].to_dict()

    for index, row in df_source.dropna(subset=['startup_name', 'investors']).iterrows():
        startup_name = row['startup_name']
        investor_list = [inv.strip() for inv in row['investors'].split(',') if inv.strip()]
        
        if startup_name in startup_id_map:
            s_id = startup_id_map[startup_name]
            # ASSUMPTION: The first funding round ID for that startup is used for simplicity
            r_id = df_funding[df_funding['startup_id'] == s_id]['round_id'].iloc[0] if not df_funding[df_funding['startup_id'] == s_id].empty else None
            
            if r_id:
                for inv_name in investor_list:
                    inv_id_row = df_investors[df_investors['name'] == inv_name]
                    if not inv_id_row.empty:
                        inv_id = inv_id_row['investor_id'].iloc[0]
                        investor_rounds.append({'round_id': r_id, 'investor_id': inv_id})
    
    if investor_rounds:
        df_round_investors = pd.DataFrame(investor_rounds).drop_duplicates()
        load_table(cursor, conn, df_round_investors, 'round_investors')
    else:
        print("No data for round_investors table.")
    
    print("\n--- Data loading complete! ---")

def load_table(cursor, conn, df, table_name):
    try:
        # Prepare the DataFrame for SQL insertion
        cols = df.columns.tolist()
        data_tuples = [tuple(row) for row in df.values]

        if not data_tuples:
             print(f"Skipping empty table: {table_name}")
             return

        insert_query = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
            sql.Identifier(table_name),
            sql.SQL(', ').join(map(sql.Identifier, cols)),
            sql.SQL(', ').join(sql.Placeholder() * len(cols))
        )

        cursor.executemany(insert_query, data_tuples)
        conn.commit()
        print(f"Loaded {len(data_tuples)} rows into {table_name}.")
    except Exception as e:
        print(f"ERROR loading data into {table_name}: {e}")
        conn.rollback()
        
def main():
    conn = None
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, 
            user=DB_USER, 
            password=DB_PASS, 
            host=DB_HOST
        )
        conn.autocommit = False # Use transactions for better control
        
        execute_sql_file(conn, 'schema.sql')

        normalize_and_load_data(conn)

    except psycopg2.OperationalError as e:
        print(f"\nFATAL ERROR: Could not connect to database '{DB_NAME}'.")
        print("Please ensure PostgreSQL is running and update DB_USER/DB_PASS in load_data.py.")
        print(f"Details: {e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()
