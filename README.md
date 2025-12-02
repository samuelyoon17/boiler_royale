# Boiler Royale: Tournament Management System

A custom tournament management backend designed to facilitate competitive Clash Royale events. While generic hosting platforms lack essential features for long-term community management, such as custom ranking algorithms, bracket seeding, and historical performance tracking, this project solves those issues. This repository houses the PostgreSQL database engine and the Python interface, forming a centralized hub where complex logic, data manipulation, and atomic transactions are handled primarily by the database layer.

## Technical Capabilities and Key Features:

* Automated Ranking System & Integrity: The system implements a custom Elo rating algorithm for dynamic matchmaking and uses a PostgreSQL Trigger (AFTER INSERT) to ensure data atomicity. This automatically recalculates and updates player ratings immediately upon match recording, eliminating race conditions and ensuring the leaderboard is always in sync with match history.
* Performance & Logic Offloading: Complex logic (such as the Elo calculation) is offloaded to the database layer using PL/pgSQL. This avoids the latency and risk associated with the application layer having to pull, process, and then push raw data back to the database.
* Robust Data Architecture: The system uses Foreign Key constraints to link matches reliably to registered users and maintains the transactional integrity of the database. The entire process is executed within atomic transactions, ensuring that if a match recording fails, no partial data is committed.
* Reporting & Tracking: The system aggregates performance statistics (wins, losses, match history) and supports dynamic leaderboards and tournament-specific filtering to retrieve up-to-date player reports.
* Tournament Management: The architecture supports the creation and administration of multi-stage tournaments and uses the Elo system for initial seeding and matchmaking.

## Tech Stack
* Language: Python
* Database: PostgreSQL
* Libraries: psycopg2 (Database Adapter)
* Concepts: ACID Transactions, Stored Procedures, Database Triggers, CTEs.

## Database Schema

**Tables**

* **users:** Stores player_tag (PK), credentials, current elo, and aggregate stats.
* **tournament:** Manages event metadata (start/end dates).
* **battles:** Transactional log of every match. Linked to users via player1_tag, player2_tag, and winner_tag.


## Engineering Journey & Challenges

This project has evolved during development as I optimized for scalability and data atomicity.

1a. Optimization: From Iterative Updates to CTEs
* Initial Approach: Originally, the update_elo logic required multiple Python calls to execute separate SQL update statements. This was inefficient and repetitive.
* Initial Solution: I refactored the SQL to use Common Table Expressions (CTEs) and CASE logic. This allowed me to select both players and update their ratings in a single query structure.

1b. Automating Logic: Triggers
* Lingering Challenge: The application layer makes a call update_elo() after record_match(). This introduced a risk of data de-synchronization if the script crashed between steps.
* Solution: I implemented PostgreSQL Triggers. Now, the moment a match is inserted, a stored procedure (update_elo_on_match_insert) fires automatically. This guarantees atomicity — a match cannot exist without the resulting rating change occurring.

2. Reporting Accuracy: Handling Null Data
* Initial Approach: When generating tournament reports, players who had not yet played a match were being excluded from results entirely when using the default INNER JOIN.
* Solution: I implemented a LEFT JOIN combined with moving the filter condition (tournament_id) into the ON clause. This preserves the user row even if match data is null. I then utilized COALESCE to convert those nulls into readable "0-0" records for the frontend/application layer.

3. Faster Search: Creating Indexes
* Initial Approach: I did not create any indexes of frequently referenced columns. As the number of users increase, this would result in slow searches. Examples include finding a user's current Elo, retrieving a player's match history, and linking battles to tournaments. Without indexing, the database would resort to slow, full-table scans.
* Solution: I created indexes on the following columns to ensure O(logn) lookup performance:
  * users.clash_royale_name and users.username: Fast login, user search, and administrative lookups.
  * battles.player1_tag and battles.player2_tag: Fetching a player's complete match history.
  * battles.tournament_id: Generating tournament-specific leaderboards and win/loss statistics.

4. Multiple Connections: Handling Database Initialization
* Challenge: PostgreSQL requires an active connection to an existing database (like the default postgres) to execute a CREATE DATABASE command. The main application client cannot assume the target database (boiler_royale_db) exists yet.
* Solution: I decoupled the logic into two specialized clients. The InitializationClient first connects to the default postgres system to create the database, then seamlessly reconnecting to the new boiler_royale_db to deploy the schema and triggers. This ensures robust deployment regardless of the initial environment state.

5. Transaction Management & Library Behaviors
* Initial Approach: While building the InitializationClient, my scripts kept failing during the CREATE DATABASE command. I discovered that the psycopg2 library adheres to Python DB-API standards by wrapping all commands in a transaction block. However, PostgreSQL architecture prevents creating databases inside a transaction block.
* Solution: I learned to use connection.autocommit = True specifically for Data Definition Language (DDL) operations. This overrides the adapter's default behavior, executing commands immediately.
* Future Considerations Application: I am choosing to keep autocommit=True for the main application logic (PostgresClient). By offloading complex updates to Database Triggers, my Python script only needs to send single, atomic INSERT commands. The database engine ensures the integrity of the Match-to-Elo chain, removing the need for complex manual transaction management in the Application Layer. If my application requires more nuanced commands, I will turn off the autocommit.

## Development Tools & AI Collaboration
To accelerate the development and validate architectural decisions, this project utilized Gemini to help with the following:
* Discovering Features: Learning about features of PostgreSQL and psycopg2 (e.g., CTEs, Triggers, COALESCE, connection.autocommit = True, User-defined Functions)
* Code Optimization: Generating and refactoring SQL + PL/pgSQL statements for improved readability and conciseness (e.g., Elo calculation in PL/pgSQL).
* Architectural Validation: Answering hypothetical scalability and concurrency questions.
* Debugging: Identified architectural flaws that would lead to NULL returns for non-participants (e.g., using INNER JOIN for get_user_tournament_info.sql). AI imposed edge cases and suggested improved SQL syntax, resulting in the implementation of LEFT JOIN and COALESCE.
* Test Data Generation: Quickly generated simulated data for userinput.txt to robustly test sequential Elo updates and specific reporting queries.
* Documentation & Presentation: Assisted in articulating technical decisions as shared in this README.

All final code, architectural decisions, and data integrity checks were verified by the developer.

## Usage
1. Prerequisites

```
Docker Desktop
Python 3.10+ installed.
```

2. Installation

In a terminal, run the following ONCE to create your postgres database:
```
docker run --name boiler_royale -e POSTGRES_USER=samuelyoon -e POSTGRES_PASSWORD=temppassword -e POSTGRES_DB=postgres -p 5432:5432 -d postgres:latest
```

Then, in your working project directory, execute the following:
```
git clone https://github.com/samuelyoon/boiler-royale.git
cd boiler-royale
```

3. Configure Environment

Create a .env file in the root directory. Update the values to match your inputs.
```
DB_HOST=localhost
DB_NAME=boiler_royale_db
DB_USER=samuelyoon
DB_PASSWORD=temppassword
DB_PORT=5432
```

4. Initialize System

Run the initialization script. This uses a dual-connection client to first connect to the system database (postgres) to create your project database, then reconnects to deploy the schema and triggers.

```
python3 -m db_manager.set_up_db
```

5. Run Operations

Execute the main script to simulate match inputs and query data:

```
python3 main.py
```

## Future Scope
* API Layer: Develop a lightweight Flask backend to serve as the application middleman, exposing core database functions (e.g., match recording, leaderboard retrieval) as RESTful API endpoints.
* Load Testing: Benchmark the trigger performance with 1,000+ concurrent match insertions.
* Full-Stack Development & Flexible Hosting: Develop a responsive web frontend to provide a user-friendly interface. Concurrently, configure the database container for flexible deployment targets - either migrating to a managed cloud service for scalability or self-hosting on a Raspberry Pi to provide a cost-effective, always-on server.
* Product Adoption & Community Impact: Introduce the fully developed system for use by a live competitive gaming community. This crucial step will provide real-world performance metrics, concurrency data, and user feedback necessary to validate the architectural choices (Triggers, Indexes) and guide future feature development.

Contact & Contribution
* Author: Samuel Yoon
* Project Link: https://github.com/samuelyoon17/boiler_royale.git
