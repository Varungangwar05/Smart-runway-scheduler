import getpass
import mysql.connector
from mysql.connector import Error


def connect_database(password):
    return mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password=password,
        database="smart_runway_db",
        connection_timeout=5
    )


def check_connection():
    password = getpass.getpass("MySQL root password: ")
    connection = None
    cursor = None

    try:
        connection = connect_database(password)
        cursor = connection.cursor()
        cursor.execute("SELECT DATABASE()")
        database_name = cursor.fetchone()[0]
        print(f"Connected successfully to: {database_name}")

    except Error as error:
        print("Connection failed:", error)

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


if __name__ == "__main__":
    check_connection()