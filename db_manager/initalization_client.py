import os

import psycopg2
from dotenv import load_dotenv


class InitalizationClient:
    def __init__(self):
        self.connection = None
        self.cursor = None
        print("Initalization Client has been created!")

    # This file is to send all SQL updates and requests to the backend

    def create_db(self):
        # Load environment variables from .env
        load_dotenv()

        # Fetch variables
        USER = os.getenv("DB_USER")
        PASSWORD = os.getenv("DB_PASSWORD")
        HOST = os.getenv("DB_HOST")
        PORT = os.getenv("DB_PORT")
        DB_NAME = "postgres"

        # Connect to the database
        try:
            connection = psycopg2.connect(
                user=USER,
                password=PASSWORD,
                host=HOST,
                port=PORT,
                dbname=DB_NAME,
                # sslmode="require",
                connect_timeout=10,
            )
            # Required for creating databases
            # Since psycpg2 wraps everything in a transaction block, autocommit
            # ensures that commands aren't wrapped and executed immediately
            connection.autocommit = True
            print("Connection successful!")
            self.connection = connection
            self.cursor = connection.cursor()
        except Exception as e:
            print(f"Failure to start connection: {e}")
            return

        tb_file_path = "sql/initialization/create_database.sql"
        command: str = ""

        try:
            with open(tb_file_path) as f:
                command = f.read()
            print("File opened successfully!")
        except IOError as e:
            print(f"Failure to open {tb_file_path}: {e}")

        try:
            print("Attempting to create database")
            self.cursor.execute(command)
            print("Tables created successfully!")
        except Exception as e:
            print(f"\033[31mFailure to create database: {e}\033[0m")

    def create_tables_triggers(self):
        # Load environment variables from .env
        load_dotenv()

        # Fetch variables
        USER = os.getenv("DB_USER")
        PASSWORD = os.getenv("DB_PASSWORD")
        HOST = os.getenv("DB_HOST")
        PORT = os.getenv("DB_PORT")
        DB_NAME = os.getenv("DB_NAME")

        # Connect to the database
        try:
            connection = psycopg2.connect(
                user=USER,
                password=PASSWORD,
                host=HOST,
                port=PORT,
                dbname=DB_NAME,
                # sslmode="require",
                connect_timeout=10,
            )
            # Required for creating tables
            # Since psycpg2 wraps everything in a transaction block, autocommit
            # ensures that commands aren't wrapped and executed immediately
            connection.autocommit = True
            print("Connection successful!")
            self.connection = connection
            self.cursor = connection.cursor()
        except Exception as e:
            print(f"Failure to start connection: {e}")
            return

        tb_file_path = "sql/initialization/create_tables.sql"
        command: str = ""

        try:
            with open(tb_file_path) as f:
                command = f.read()
            print("File opened successfully!")
        except IOError as e:
            print(f"Failure to open {tb_file_path}: {e}")

        try:
            print("Attempting to create tables")
            self.cursor.execute(command)
            print("Tables created successfully!")
        except Exception as e:
            print(f"\033[31mFailure to create tables: {e}\033[0m")

        tb_file_path = "sql/initialization/create_triggers.sql"
        command: str = ""

        try:
            with open(tb_file_path) as f:
                command = f.read()
            print("File opened successfully!")
        except IOError as e:
            print(f"Failure to open {tb_file_path}: {e}")

        try:
            print("Attempting to create triggers")
            self.cursor.execute(command)
            print("Triggers created successfully!")
        except Exception as e:
            print(f"\033[31mFailure to create triggers: {e}\033[0m")

    def close_connection(self):
        try:
            self.cursor.close()
            self.connection.close()
            print("Connection closed successfully")
        except Exception as e:
            print(f"Connection and/or cursor closed unsuccessfully: {e}")
