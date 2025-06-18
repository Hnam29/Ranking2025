#!/usr/bin/env python3
"""
Test script to verify environment variables are loaded correctly
and database connection works with the new secure configuration.
"""

import os
from dotenv import load_dotenv

def test_env_variables():
    """Test if environment variables are loaded correctly."""
    print("Testing environment variable loading...")
    
    # Load environment variables
    load_dotenv()
    
    # Check if all required variables are present
    required_vars = ['DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_DATABASE', 'DB_PORT']
    
    print("\n--- Environment Variables Check ---")
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mask password for security
            if 'PASSWORD' in var:
                print(f"✅ {var}: {'*' * len(value)}")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: NOT SET")
    
    # Check SSL certificate path
    ssl_path = os.getenv('SSL_CA_PATH')
    if ssl_path:
        if os.path.exists(ssl_path):
            print(f"✅ SSL_CA_PATH: {ssl_path} (file exists)")
        else:
            print(f"⚠️  SSL_CA_PATH: {ssl_path} (file not found)")
    else:
        print("❌ SSL_CA_PATH: NOT SET")

def test_database_connection():
    """Test database connection using the new configuration."""
    print("\n--- Database Connection Test ---")
    
    try:
        # Import the updated database module
        from get_data_from_db import execute_sql_to_dataframe
        
        # Test with a simple query
        test_query = "SELECT 1 as test_connection"
        result = execute_sql_to_dataframe(test_query)
        
        if result is not None and len(result) > 0:
            print("✅ Database connection successful!")
            print(f"✅ Test query result: {result.iloc[0, 0]}")
        else:
            print("❌ Database connection failed - no results returned")
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")

if __name__ == "__main__":
    print("🔒 Secure Database Configuration Test")
    print("=" * 50)
    
    test_env_variables()
    test_database_connection()
    
    print("\n" + "=" * 50)
    print("Test completed!")
