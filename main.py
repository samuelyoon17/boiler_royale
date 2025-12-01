from db_manager import postgres_client as client


def main():
    br = client.PostgresClient()

    with open("sample_data/userinput.txt") as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]

        for i in range(0, len(lines), 2):
            action = lines[i].lower()
            data = lines[i + 1]

            if action == "add_user":
                print("\nAdding user")
                br.run_command("sql/add_user.sql", data)

            elif action == "record_match":
                print("\nRecording match")
                br.run_command("sql/record_match.sql", data)

            elif action == "add_tournament":
                print("\nAdding tournament")
                br.run_command("sql/add_tournament.sql", data)

            elif action == "get_leaderboard":
                print("\nGetting leaderboard")
                results = br.run_command("sql/get_leaderboard.sql", data)

                if results is not None:
                    for element in results:
                        print(element)

            elif action == "get_tournament_players":
                print("\nGetting tournament pool of players")
                results = br.run_command("sql/get_tournament_players.sql", data)

                if results is not None:
                    for element in results:
                        print(element)

            elif action == "get_user_tournament_info":
                print("\nGetting user data from tournament")
                results = br.run_command("sql/get_user_tournament_info.sql", data)

                if results is not None:
                    print(results)

    br.close_connection()


if __name__ == "__main__":
    main()
