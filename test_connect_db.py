import mysql.connector

conn = mysql.connector.connect(
    host="13.214.140.159",
    port=3306,
    user="edte_admin",
    password="vNN*+2%Du@idhH%w",
    database="edte_EA_Ranking2025"

    # host="localhost",
    # port=3306,
    # user="root",
    # password="HnAm2002#@!",
    # database="EdtechAgency_Ranking2025"
)

cursor = conn.cursor()
cursor.execute("SELECT NOW();")
print("Connected! Server time:", cursor.fetchone())

cursor.close()
conn.close()




# import mysql.connector
# from mysql.connector import Error

# try:
#     # Establish connection
#     connection = mysql.connector.connect(
#         host="13.214.140.159",
#         user="edte_admin",
#         password="vNN*+2%Du@idhH%w",
#         database="edte_EA_Ranking2025",
#         port=3306,
#     )
    
#     if connection.is_connected():
#         print("Connection successful")

#         # Create a cursor to execute SQL queries
#         cursor = connection.cursor()

#         # Create a test table
#         create_table_query = """
#         CREATE TABLE IF NOT EXISTS test_table (
#             id INT AUTO_INCREMENT PRIMARY KEY,
#             name VARCHAR(255) NOT NULL,
#             age INT
#         );
#         """
#         cursor.execute(create_table_query)
#         print("Test table created successfully")

#         # Insert test data into the table
#         insert_data_query = """
#         INSERT INTO test_table (name, age)
#         VALUES (%s, %s);
#         """
#         data = [("Alice", 30), ("Bob", 25), ("Charlie", 35)]
#         cursor.executemany(insert_data_query, data)
#         connection.commit()
#         print("Test data inserted successfully")

#         # Close the cursor
#         cursor.close()

#     connection.close()

# except Error as e:
#     print(f"Error: {e}")


# import mysql.connector
# from mysql.connector import Error

# try:
#     # Establish connection with UTF-8 encoding
#     connection = mysql.connector.connect(
#         host="13.214.140.159",
#         user="edte_admin",
#         password="vNN*+2%Du@idhH%w",
#         database="edte_EA_Ranking2025",
#         port=3306,
#         charset='utf8mb4'
#     )

#     if connection.is_connected():
#         print("Connection successful")
#         cursor = connection.cursor()

#         # --- Check Database Collation ---
#         cursor.execute("SELECT DEFAULT_CHARACTER_SET_NAME, DEFAULT_COLLATION_NAME FROM information_schema.SCHEMATA WHERE SCHEMA_NAME = %s", (connection.database,))
#         db_collation = cursor.fetchone()
#         print(f"\nDatabase Collation:")
#         if db_collation:
#             print(f"  Character Set: {db_collation[0]}")
#             print(f"  Collation:     {db_collation[1]}")
#         else:
#             print(f"  Could not retrieve database collation.")

#         # --- Check Table Collation ---
#         cursor.execute("SHOW TABLE STATUS LIKE %s", ('fact_ranking_app_review',))
#         table_status = cursor.fetchone()
#         print(f"\nTable 'fact_ranking_app_review' Collation:")
#         if table_status:
#             print(f"  Collation:     {table_status[17]}") # Collation is usually at index 17
#         else:
#             print(f"  Table 'fact_ranking_app_review' not found.")

#         # --- Check 'content' Column Collation ---
#         cursor.execute("SHOW FULL COLUMNS FROM fact_ranking_app_review LIKE 'content'")
#         column_info = cursor.fetchone()
#         print(f"\n'content' Column Collation:")
#         if column_info:
#             print(f"  Collation:     {column_info[1]}") # Collation is usually at index 1
#         else:
#             print(f"  'content' column not found in 'fact_ranking_app_review' table.")

#         # Close the cursor
#         cursor.close()

#     connection.close()

# except Error as e:
#     print(f"Error: {e}")
# finally:
#     if 'connection' in locals() and connection.is_connected():
#         connection.close()
#         print("Database connection closed.")