import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import os

print("Initializing SQLite database module...")

# --- SQLite Configuration ---
db_path = 'EA_Ranking2025.db'  
os.makedirs(os.path.dirname(db_path), exist_ok=True)  # Ensure directory exists

# --- Engine Creation Helper ---
def _get_sqlite_engine(db_file_path: str):
    """
    Creates a SQLAlchemy engine for an SQLite database.
    
    Args:
        db_file_path (str): Path to the SQLite .db file.
    
    Returns:
        SQLAlchemy Engine object or None if failed.
    """
    try:
        conn_str = f"sqlite:///{db_file_path}"
        eng = create_engine(conn_str)
        # Test connection on creation
        with eng.connect() as conn:
            print(f"Connected to SQLite database at '{db_file_path}'.")
        return eng
    except Exception as e:
        print(f"FATAL: Error creating SQLite engine: {e}")
        return None

# --- Create Engine ONCE when module is imported ---
engine = _get_sqlite_engine(db_path)

if engine is None:
    print("Failed to initialize SQLite engine. Exiting module setup.")

# --- Main Function to Export ---
def execute_sql_to_dataframe(sql_query: str, params=None):
    global engine
    if engine is None:
        print("Error: Database engine is not available (initialization failed?).")
        return None

    print("-" * 30)
    print(f"Executing SQL query:\n{sql_query}")
    if params:
        print(f"With parameters: {params}")
    print("-" * 30)

    try:
        stmt = text(sql_query)
        df = pd.read_sql(stmt, con=engine, params=params)
        print(f"Query executed successfully. Retrieved {len(df)} rows.")
        return df
    except SQLAlchemyError as db_err:
        print(f"SQLAlchemy Error executing query: {db_err}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

# --- Function for DDL/DML statements ---
def execute_sql_ddl(sql_query: str, params=None):
    global engine
    if engine is None:
        print("Error: Database engine is not available.")
        return False

    print("-" * 30)
    print(f"Executing SQL DDL/DML statement:\n{sql_query}")
    if params:
        print(f"With parameters: {params}")
    print("-" * 30)

    try:
        with engine.connect() as connection:
            stmt = text(sql_query)
            connection.execute(stmt, params or {})
            connection.commit()
        print("Statement executed successfully.")
        return True
    except SQLAlchemyError as db_err:
        print(f"SQLAlchemy Error: {db_err}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

print("SQLite database module initialized.")