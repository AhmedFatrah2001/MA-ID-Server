import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

def create_connection():
    """
    Create a database connection to MySQL using credentials from .env file.
    """
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            port=os.getenv("DB_PORT", 3306)  # Default port is 3306
        )
        if connection.is_connected():
            print("MySQL Database connection successful")
            return connection
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None

def close_connection(connection):
    """
    Close the given MySQL connection.
    """
    if connection and connection.is_connected():
        connection.close()
        print("MySQL connection closed")

def create_users_table():
    """
    Create a 'users' table if it doesn't exist.
    """
    create_table_query = """
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) NOT NULL UNIQUE,
        email VARCHAR(50) NOT NULL UNIQUE,
        password VARCHAR(255) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute(create_table_query)
            print("Users table created successfully")
        except Error as e:
            print(f"Error creating table: {e}")
        finally:
            cursor.close()
            close_connection(connection)

# Test the connection and table creation
if __name__ == "__main__":
    create_users_table()
