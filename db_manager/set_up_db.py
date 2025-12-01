from db_manager.initalization_client import InitalizationClient

# To execute run the following in ~/projects/boiler_royale
# python3 -m db_manager.set_up_db


# The following command should be ran ONCE to establish Docker SQL DB
# docker run --name boiler_royale -e POSTGRES_USER=samuelyoon -e POSTGRES_PASSWORD=temppassword -e POSTGRES_DB=boiler_royale_db -p 5432:5432 -d postgres:latest
#
# 11/24/2025
# Added create_db() method for deployment anywhere
# Assumption: DB and Tables don't exist
def main():
    set_up_client = InitalizationClient()
    set_up_client.create_db()
    set_up_client.create_tables_triggers()
    set_up_client.close_connection()


if __name__ == "__main__":
    main()
