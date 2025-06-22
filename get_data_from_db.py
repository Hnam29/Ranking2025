# import pandas as pd
# from sqlalchemy import create_engine # For type hinting or if creating engine inside
# from sqlalchemy.exc import SQLAlchemyError # For specific error handling
# import urllib.parse # If creating engine inside or as helper

# db_config = {
#     'user': 'root',
#     'password': 'HnAm2002#@!',
#     'host': 'localhost',
#     'database': 'EdtechAgency_Ranking2025', 
# }

# def get_configured_engine(config):
#     """Helper to create/get the engine (optional)."""
#     try:
#         encoded_password = urllib.parse.quote_plus(config['password'])
#         # Make sure to use the correct driver (pymysql recommended)
#         conn_str = (
#             f"mysql+pymysql://"
#             f"{config['user']}:{encoded_password}"
#             f"@{config['host']}:{config['port']}"
#             f"/{config['database']}"
#             f"?charset=utf8mb4"
#         )
#         eng = create_engine(conn_str)
#         # Test connection
#         with eng.connect() as conn:
#             print(f"Engine connection successful to '{config['database']}'.")
#         return eng
#     except Exception as e:
#         print(f"Error creating database engine: {e}")
#         return None

# # Create the engine once (e.g., globally or pass config to the function)
# engine = get_configured_engine(db_config)

# def execute_sql_to_dataframe(sql_query: str, engine):
#     """
#     Executes a SQL query against the database using the provided SQLAlchemy engine
#     and returns the result as a pandas DataFrame.

#     Args:
#         sql_query (str): The SQL query string to execute.
#         engine: An active SQLAlchemy engine object connected to the target database.
#                 (Must be created beforehand, e.g., using create_engine).

#     Returns:
#         pandas.DataFrame: A DataFrame containing the query results.
#                         Returns an empty DataFrame if the query is valid but retrieves no rows.
#                         Returns None if an error occurs during connection or query execution.
#     """
#     if engine is None:
#         print("Error: Invalid database engine provided.")
#         return None

#     print("-" * 30)
#     print(f"Executing SQL query:")
#     # Print first 500 chars of query for logging, add '...' if longer
#     print(f"{sql_query[:500]}{'...' if len(sql_query) > 500 else ''}")
#     print("-" * 30)

#     try:
#         # Use pandas.read_sql for direct DataFrame creation from engine
#         df = pd.read_sql(sql_query, con=engine)
#         print(f"Query executed successfully. Retrieved {len(df)} rows.")
#         return df

#     # Handle potential database errors during query execution
#     except SQLAlchemyError as db_err:
#         print(f"SQLAlchemy Database Error executing query: {db_err}")
#         return None
#     # Handle other potential exceptions
#     except Exception as e:
#         print(f"An unexpected error occurred: {e}")
#         return None

# ########### HOW TO USE ###########
# # IMPORTANT: Make sure 'engine' is defined and valid before calling the function.
# # Using the global 'engine' created by get_configured_engine or your previous setup.

# # if 'engine' in locals() and engine is not None: # Check if engine exists and is valid

# #     query_web_sample = "SELECT edtech_url, web_col1 FROM dim_ranking_web LIMIT 10;"
# #     df_web_sample = execute_sql_to_dataframe(query_web_sample, engine)

# #     if df_web_sample is not None:
# #         print("\n--- Sample Web Dimension Data ---")
# #         print(df_web_sample.head())
# #     else:
# #         print("\nFailed to retrieve web dimension sample.")

# # else:
# #     print("\nDatabase engine is not configured. Cannot run examples.")






# File: extract_data_from_db.py

import pandas as pd
import os
import sys

# Try to import database dependencies
try:
    from sqlalchemy import create_engine, text
    from sqlalchemy.exc import SQLAlchemyError
    import urllib.parse
    import pymysql
    from dotenv import load_dotenv
    DB_DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    print(f"Database dependencies not available: {e}")
    DB_DEPENDENCIES_AVAILABLE = False

print("Initializing database module...") # See when this runs

if DB_DEPENDENCIES_AVAILABLE:
    # Load environment variables from .env file
    load_dotenv()

    # --- Database Configuration ---
    # Using environment variables for security
    db_config = {
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'host': os.getenv('DB_HOST'),
        'database': os.getenv('DB_DATABASE'),
        'port': int(os.getenv('DB_PORT', 3306))  # Default to 3306 if not specified
    }

    # Check if all required environment variables are present
    if not all(db_config.values()):
        print("Warning: Some database environment variables are missing.")
        print("Available config:", {k: v for k, v in db_config.items() if v})
        DB_DEPENDENCIES_AVAILABLE = False
else:
    db_config = {}

# --- Engine Creation Helper ---
def _get_configured_engine(config): # Made 'private' by convention with _
    """Helper to create the engine."""
    if not DB_DEPENDENCIES_AVAILABLE:
        print("Database dependencies not available. Cannot create engine.")
        return None

    required_keys = ['user', 'password', 'host', 'port', 'database']
    if not all(key in config for key in required_keys):
        print(f"Error: db_config is missing one or more keys: {required_keys}")
        return None

    # Check for None values
    if not all(config.get(key) for key in required_keys):
        print(f"Error: Some database configuration values are None or empty")
        return None

    try:
        encoded_password = urllib.parse.quote_plus(config['password'])
        # Using PyMySQL driver (recommended)
        ssl_ca_path = os.getenv('SSL_CA_PATH', '')

        # Build connection string
        conn_str = (
            f"mysql+pymysql://"
            f"{config['user']}:{encoded_password}"
            f"@{config['host']}:{config['port']}"
            f"/{config['database']}"
            f"?charset=utf8mb4"
        )

        # Add SSL if path is provided
        if ssl_ca_path and os.path.exists(ssl_ca_path):
            conn_str += f"&ssl_ca={ssl_ca_path}"

        eng = create_engine(conn_str, pool_recycle=3600) # pool_recycle helps with long-running apps
        # Test connection on creation
        with eng.connect() as conn:
            print(f"Database engine connection successful to '{config['database']}'.")
        return eng
    except Exception as e:
        print(f"Error creating database engine: {e}")
        return None

# --- Create Engine ONCE when module is imported ---
if DB_DEPENDENCIES_AVAILABLE:
    engine = _get_configured_engine(db_config)
else:
    engine = None

# Handle engine creation failure gracefully
if engine is None:
    print("Database engine not available. Database functions will return None.")
    # Don't exit - just continue with limited functionality

# --- Main Function to Export ---
def execute_sql_to_dataframe(sql_query: str, params=None):
    """
    Executes a SQL query against the pre-configured database engine
    and returns the result as a pandas DataFrame.

    Args:
        sql_query (str): The SQL query string to execute.
                         Use :param_name for parameter binding.
        params (dict, optional): Dictionary of parameters to bind to the query.
                                 Example: {"user_id": 101, "status": "active"}

    Returns:
        pandas.DataFrame: A DataFrame containing the query results.
                          Returns an empty DataFrame if the query is valid but retrieves no rows.
                          Returns None if the engine is invalid or an error occurs.
    """
    global engine # Access the engine created when the module was loaded
    if not DB_DEPENDENCIES_AVAILABLE or engine is None:
        print("Warning: Database engine is not available. Returning empty DataFrame.")
        return pd.DataFrame()  # Return empty DataFrame instead of None

    print("-" * 30)
    print(f"Executing SQL query:")
    print(f"{sql_query[:500]}{'...' if len(sql_query) > 500 else ''}")
    if params:
        print(f"With parameters: {params}")
    print("-" * 30)

    try:
        # Use text() for passing parameters safely
        stmt = text(sql_query)
        # Use pandas.read_sql with the global engine
        # Pass parameters if they exist
        df = pd.read_sql(stmt, con=engine, params=params)
        print(f"Query executed successfully. Retrieved {len(df)} rows.")
        return df

    except SQLAlchemyError as db_err:
        print(f"SQLAlchemy Database Error executing query: {db_err}")
        return pd.DataFrame()  # Return empty DataFrame instead of None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return pd.DataFrame()  # Return empty DataFrame instead of None

# --- Optional: Add other database-related functions here ---
def execute_sql_ddl(sql_query: str, params=None):
    """
    Thực thi câu lệnh SQL DDL (Data Definition Language) hoặc DML (Data Manipulation Language)
    không trả về dữ liệu như CREATE, ALTER, DROP, INSERT, UPDATE, DELETE, etc.

    Args:
        sql_query (str): Câu lệnh SQL cần thực thi.
                         Sử dụng :param_name cho việc binding tham số.
        params (dict, optional): Dictionary chứa các tham số để binding vào câu lệnh.
                                 Ví dụ: {"user_id": 101, "status": "active"}

    Returns:
        bool: True nếu thực thi thành công, False nếu có lỗi.
    """
    global engine  # Truy cập engine đã được tạo khi module được load
    if not DB_DEPENDENCIES_AVAILABLE or engine is None:
        print("Warning: Database engine không khả dụng. DDL command skipped.")
        return False

    print("-" * 30)
    print(f"Đang thực thi câu lệnh SQL DDL:")
    print(f"{sql_query[:500]}{'...' if len(sql_query) > 500 else ''}")
    if params:
        print(f"Với tham số: {params}")
    print("-" * 30)

    try:
        # Tạo connection từ engine
        with engine.connect() as connection:
            # Sử dụng text() để truyền tham số an toàn
            stmt = text(sql_query)

            # Thực thi câu lệnh
            if params:
                connection.execute(stmt, params)
            else:
                connection.execute(stmt)

            # Commit để đảm bảo các thay đổi được lưu lại
            connection.commit()

        print(f"Câu lệnh đã được thực thi thành công.")
        return True

    except SQLAlchemyError as db_err:
        print(f"Lỗi SQLAlchemy khi thực thi câu lệnh: {db_err}")
        return False
    except Exception as e:
        print(f"Một lỗi không mong đợi đã xảy ra: {e}")
        return False
    
print("Database module initialized.") # See when this runs