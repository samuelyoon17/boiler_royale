import ast
import os

import psycopg2
from dotenv import load_dotenv

GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"


# This file is to send all SQL updates and requests to the backend
class PostgresClient:
    def __init__(self):
        self.connection, self.cursor = self.start_connection()

    # This file is to send all SQL updates and requests to the backend
    def start_connection(self):
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
            connection.autocommit = True

            print(f"{GREEN}Connection successful!{RESET}")
            return connection, connection.cursor()
        except Exception as e:
            print(f"{RED}Failure to start connection: {e}{RESET}")
            return None, None

    def close_connection(self):
        try:
            self.cursor.close()
            self.connection.close()
            print(f"{GREEN}Connection closed successfully!{RESET}")
        except Exception as e:
            print(f"{RED}Connection and/or cursor closed unsuccessfully: {e}{RESET}")

    # Create multiple run commands and have each instance use their own fields of connection and cursor
    # to stop passing in the same field
    def run_command(self, file_path: str, input_data=None):
        """
        args:
            input_data: data is guarenteed to be valid
        """
        command = ""
        results = None
        try:
            with open(file_path) as f:
                command = f.read()
            print(f"{GREEN}File opened successfully!{RESET}")
        except IOError as e:
            print(f"{RED}Failure to open {file_path}: {e}{RESET}")
            results = None

        if command:
            input_data = () if input_data is None else ast.literal_eval(input_data)

            try:
                self.cursor.execute(command, input_data)

                if self.cursor.description is not None:
                    results = self.cursor.fetchall()

                print(f"{GREEN}Command executed successfully!{RESET}")
            except Exception as e:
                self.connection.rollback()
                print(f"{RED}Execution failure: {e}{RESET}")
                results = None

        return results
