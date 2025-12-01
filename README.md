# Boiler Royale: Tournament Management System

A custom tournament management backend designed to facilitate competitive Clash Royale events. While generic hosting platforms lack essential features for long-term community management, such as custom ranking algorithms, bracket seeding, and historical performance tracking, this project solves those issues. This repository houses the PostgreSQL database engine and the Python interface, forming a centralized hub where complex logic, data manipulation, and atomic transactions are handled primarily by the database layer.

## Technical Capabilities and Key Features:

* Automated Ranking System & Integrity: The system implements a custom Elo rating algorithm for dynamic matchmaking and uses a PostgreSQL Trigger (AFTER INSERT) to ensure data validity. This automatically recalculates and updates player ratings immediately upon match recording, eliminating race conditions and ensuring the leaderboard is always in sync with match history.
* Performance & Logic Offloading: Complex logic (such as the Elo calculation) is offloaded to the database layer using PL/pgSQL and CTEs. This avoids the latency and risk associated with the application layer having to pull, process, and then push raw data back to the database.
* Robust Data Architecture: The system uses Foreign Key constraints to link matches reliably to registered users and maintains the transactional integrity of the database. The entire process is executed within atomic transactions, ensuring that if a match recording fails, no partial data is committed.
* Reporting & Tracking: The system aggregates granular performance statistics (wins, losses, match history) and supports dynamic leaderboards and tournament-specific filtering to retrieve up-to-date player reports.
* Tournament Management: The architecture supports the creation and administration of multi-stage tournaments and uses the Elo system for initial seeding and matchmaking.

## Tech Stack
* Language: Python
* Database: PostgreSQL
* Libraries: psycopg2 (Database Adapter)
* Concepts: ACID Transactions, Stored Procedures, Database Triggers, CTEs, RESTful Architecture principles.

## Database Schema

* **users:** Stores player_tag (PK), credentials, current elo, and aggregate stats.
* **tournament:** Manages event metadata (start/end dates).
* **battles:** Transactional log of every match. Linked to users via player1_tag, player2_tag, and winner_tag.


## Engineering Journey & Challenges

This project evolved significantly during development as I optimized for scalability and data correctness.

1a. Optimization: From Iterative Updates to CTEs
* Initial Approach: Originally, the update_elo logic required multiple Python calls to execute separate SQL update statements. This was inefficient and repetitive.
* Initial Solution: I refactored the SQL to use Common Table Expressions (CTEs) and CASE logic. This allowed me to select both players and update their ratings in a single query structure.

1b. Automating Logic: Triggers
* Lingering Challenge: The application layer makes a call update_elo() after record_match(). This introduced a risk of data de-synchronization if the script crashed between steps.
* Solution: I implemented PostgreSQL Triggers. Now, the moment a match is inserted, a stored procedure (update_elo_on_match_insert) fires automatically. This guarantees atomicity — a match cannot exist without the resulting rating change occurring.

2. Reporting Accuracy: Handling Null Data
* Initial Approach: When generating tournament reports, players who had not yet played a match were being excluded from results entirely when using the standard INNER JOIN.
* Solution: I implemented a LEFT JOIN combined with moving the filter condition (tournament_id) into the ON clause. This preserves the user row even if match data is null. I then utilized COALESCE to convert those nulls into readable "0-0" records for the frontend/application layer.

3. Faster Search: Creating Indexes
* Initial Approach: I did not create any indexes of frequently referenced columns. As the number of users increase, this would result in slow searches.
* Solution: I created indexes on 

4. Multiple Connections: Handling Database Initialization
* Challenge: PostgreSQL requires an active connection to an existing database (like the default postgres) to execute a CREATE DATABASE command. The main application client cannot assume the target database (boiler_royale_db) exists yet.
* Solution: I decoupled the logic into two specialized clients. The InitializationClient first connects to the default postgres system to create the database, then seamlessly reconnecting to the new boiler_royale_db to deploy the schema and triggers. This ensures robust deployment regardless of the initial environment state.

## Setup & Usage

Prerequisites

```
PostgreSQL installed locally.
Python 3.x installed.
```

Installation
```
git clone https://github.com/samuelyoon/boiler-royale.git
cd boiler-royale
```

Set up environment variables Create a .env file in the root directory:

```
DB_HOST=localhost
DB_NAME=boiler_royale_db
DB_USER=your_username
DB_PASSWORD=your_password
DB_PORT=5432
```

Initialize the Database, Tables, and Triggers:

```
python3 -m db_manager.set_up_db
```

Run database operations with main.py to simulate match inputs (currently via sample_data/userinput.txt):

```
python3 main.py
```


## Future Scope
* API Layer: Develop a lightweight Flask/FastAPI wrapper to expose these SQL functions as RESTful endpoints.
* Load Testing: Benchmark the trigger performance with 10,000+ concurrent match insertions.
* Frontend Development: Create the other half of this project by making a website that connects to this database hosted on a non-local machine.

Contact & Contribution
* Author: Samuel Yoon
* Project Link: [GitHub Repository Link]
