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
from sqlalchemy import create_engine, text # Added 'text' for parameter binding if needed later
from sqlalchemy.exc import SQLAlchemyError
import urllib.parse
import sys # To potentially exit if engine creation fails

print("Initializing database module...") # See when this runs

# --- Database Configuration ---
db_config = {
    'user': 'root',
    'password': 'HnAm2002#@!',
    'host': 'localhost',
    'port': 3306,  # Added default MySQL port
    'database': 'EdtechAgency_Ranking2025',
}

# --- Engine Creation Helper ---
def _get_configured_engine(config): # Made 'private' by convention with _
    """Helper to create the engine."""
    required_keys = ['user', 'password', 'host', 'port', 'database']
    if not all(key in config for key in required_keys):
        print(f"Error: db_config is missing one or more keys: {required_keys}")
        return None
    try:
        encoded_password = urllib.parse.quote_plus(config['password'])
        # Using PyMySQL driver (recommended)
        conn_str = (
            f"mysql+pymysql://"
            f"{config['user']}:{encoded_password}"
            f"@{config['host']}:{config['port']}"
            f"/{config['database']}"
            f"?charset=utf8mb4"
        )
        eng = create_engine(conn_str, pool_recycle=3600) # pool_recycle helps with long-running apps
        # Test connection on creation
        with eng.connect() as conn:
            print(f"Database engine connection successful to '{config['database']}'.")
        return eng
    except Exception as e:
        print(f"FATAL: Error creating database engine: {e}")
        return None

# --- Create Engine ONCE when module is imported ---
engine = _get_configured_engine(db_config)

# Exit script/module loading if engine creation failed critically
if engine is None:
    print("Failed to initialize database engine. Exiting module setup.")
    # Depending on usage, you might raise an exception or handle this differently
    # For simplicity here, functions below will just check if engine is None.
    # sys.exit("Database connection could not be established.") # Use this for critical failure

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
    if engine is None:
        print("Error: Database engine is not available (initialization failed?).")
        return None

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
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

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
    if engine is None:
        print("Lỗi: Database engine không khả dụng (khởi tạo thất bại?).")
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