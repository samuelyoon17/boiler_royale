# Boiler Royale: Tournament Management System

A custom tournament management backend designed to facilitate competitive Clash Royale events. While generic hosting platforms lack essential features for long-term community management, such as custom ranking algorithms, bracket seeding, and historical performance tracking, this project solves those issues. This repository houses the PostgreSQL database engine and the Python interface, forming a centralized hub where complex logic, data manipulation, and atomic transactions are handled primarily by the database layer.

## Technical Capabilities and Key Features

### **Automated Ranking System & Integrity**
- Implements a custom Elo rating algorithm for dynamic player matchmaking.
- Uses a PostgreSQL `AFTER INSERT` trigger to ensure data atomicity and immediately recalculate ratings when new matches are recorded.
- Automatically keeps the leaderboard consistent with match history by eliminating race conditions and preventing stale data.

### **Performance & Logic Offloading**
- Complex logic, such as Elo updates, is pushed down to the database layer using **PL/pgSQL**.
- Avoids the overhead and risk of pulling raw data into the application layer for computation.
- Reduces latency and ensures computations occur where the data already lives.

### **Robust Data Architecture**
- Enforces consistency with **Foreign Key constraints** linking matches to registered users.
- Executes all match recordings within **atomic transactions** so no partial or corrupt data ever persists.
- Ensures that failed inserts cleanly roll back, preserving database integrity.

### **Reporting & Tracking**
- Aggregates game statistics such as wins, losses, and detailed match history.
- Supports dynamic leaderboards and tournament-aware filtering to produce real-time reports for any player or event.

### **Tournament Management**
- Supports full lifecycle administration of multi-stage tournaments.
- Uses Elo for seeding to ensure fair progression through each stage.

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

### 1. Optimization and Automating Logic: From Iterative Updates to CTEs to Triggers
* **Initial Approach:** Originally, the `update_elo` logic required multiple Python calls to execute separate SQL update statements. This was inefficient and repetitive.
* **Initial Solution:** I refactored the SQL to use Common Table Expressions (CTEs) and `CASE` logic. This allowed me to select both players and update their ratings in a single query structure.
* **Lingering Challenge:** The application layer made a call to `update_elo()` after `record_match()`. This introduced a risk of data de-synchronization if the script crashed between steps.
* **Solution:** I implemented PostgreSQL Triggers. Now, the moment a match is inserted, a stored procedure (`update_elo_on_match_insert`) fires automatically. This guarantees atomicity because a match cannot exist without the resulting rating change occurring.

### 2. Reporting Accuracy: Handling Null Data
* **Initial Approach:** When generating tournament reports, players who had not yet played a match were being excluded entirely when using the default `INNER JOIN`.
* **Solution:** I implemented a `LEFT JOIN` combined with moving the filter condition (`tournament_id`) into the `ON` clause. This preserves the user row even if match data is null. I then utilized `COALESCE` to convert those nulls into readable `"0-0"` records for the frontend/application layer.

### 3. Faster Search: Creating Indexes
* **Initial Approach:** I did not create any indexes on frequently referenced columns. As the number of users increased, this would result in slow searches. Examples include finding a user's current Elo, retrieving a player's match history, and linking battles to tournaments. Without indexing, the database would resort to slow, full-table scans.
* **Solution:** I created indexes on the following columns to ensure `O(log n)` lookup performance:
  * `users.clash_royale_name` and `users.username`: Fast login, user search, and administrative lookups.
  * `battles.player1_tag` and `battles.player2_tag`: Fetching a player's complete match history.
  * `battles.tournament_id`: Generating tournament-specific leaderboards and win/loss statistics.

### 4. Multiple Connections: Handling Database Initialization
* **Challenge:** PostgreSQL requires an active connection to an existing database (like the default `postgres`) to execute a `CREATE DATABASE` command. The main application client cannot assume the target database (`boiler_royale_db`) exists yet.
* **Solution:** I decoupled the logic into two specialized clients. The `InitializationClient` first connects to the default `postgres` system to create the database, then seamlessly reconnects to the new `boiler_royale_db` to deploy the schema and triggers. This ensures robust deployment regardless of the initial environment state.

### 5. Transaction Management & Library Behaviors
* **Initial Approach:** While building the `InitializationClient`, my scripts kept failing during the `CREATE DATABASE` command. I discovered that the `psycopg2` library adheres to Python DB-API standards by wrapping all commands in a transaction block. However, PostgreSQL architecture prevents creating databases inside a transaction block.
* **Solution:** I learned to use `connection.autocommit = True` specifically for Data Definition Language (DDL) operations. This overrides the adapter's default behavior, executing commands immediately.

* **Future Considerations:** I am choosing to keep `autocommit=True` for the main application logic (`PostgresClient`). By offloading complex updates to Database Triggers, my Python script only needs to send single, atomic `INSERT` commands. The database engine ensures the integrity of the Match-to-Elo chain, removing the need for complex manual transaction management in the Application Layer. If my application requires more nuanced commands, I will turn off autocommit.



## Development Tools & AI Collaboration
To accelerate development and validate architectural decisions, this project leveraged AI assistance for the following:

### **Discovering Features**
- Learned advanced PostgreSQL and `psycopg2` features including CTEs, Triggers, `COALESCE`, `connection.autocommit = True`, and user-defined functions.

### **Code Optimization**
- Refactored SQL and PL/pgSQL logic for readability and conciseness (e.g., Elo calculation).

### **Architectural Validation**
- Explored scalability, concurrency, and performance trade-offs through hypothetical design questions.

### **Debugging Assistance**
- Identified flaws such as missing rows for users who hadn’t played yet due to incorrect `INNER JOIN` usage.
- Led to implementing `LEFT JOIN` + `COALESCE` for accurate tournament reporting.

### **Test Data Generation**
- Quickly generated simulated match sequences for `userinput.txt`, enabling robust testing of sequential Elo updates and reporting pipelines.

### **Documentation & Presentation**
- Helped articulate and structure technical decisions throughout this README.


### Rejected AI Ideas
While I accepted some suggestions from Gemini, I rejected others as they did not align with my project goals and introduced technical issues:

#### 1. Application-Layer Transaction Management
* **Suggestion:** The AI recommended the standard Python practice of using `autocommit=False` and manually managing `commit()/rollback()` blocks in the application layer to ensure ACID compliance.
* **My Decision:** I rejected this in favor of `autocommit=True` combined with PostgreSQL Triggers.
* **Rationale:** Manual transaction management in Python introduces complexity and the risk of non-atomic transactions if part of the system crashes. By offloading atomicity to the database, I ensured that data integrity is enforced by the server itself, not the client, guaranteeing that a Match Record and Elo Update always happen simultaneously regardless of client-side failures.

#### 2. Architecture Strategy: Modular SQL & Deterministic Simulation
* **Standard Suggestion:** The AI recommended hardcoding SQL queries as inline strings within Python functions for rapid development.
* **Issue:** This is common for quick scripting, but it tightly integrates database logic into application code.
* **My Decision:** I designed a Modular Command Architecture. All SQL queries are stored in dedicated `.sql` files, and a Python command loop (`main.py`) processes a structured `input.txt` file that defines high-level commands (e.g., `INSERT_MATCH`, `UPDATE_ELO`) followed by their required parameters. Each command maps directly to and executes its corresponding SQL file.
* **Rationale:** This design achieves three software engineering goals:

##### 1. Deterministic Simulation & Backtesting
I treat the tournament system like a deterministic simulation: the same input file always produces the same results.

- I can write complex, controlled match sequences (e.g., 50 games in an exact order) directly in `input.txt`.
- The system processes them line-by-line through the command loop, making every test repeatable.
- This allows me to repeatedly backtest changes to the Elo algorithm (e.g., adjusting the K-factor, modifying expected-score formulas, adding integrity checks) using the exact same sequence of matches.
- By comparing outputs across these runs, I can evaluate whether rating progression feels **natural, stable, and fair**:
  - Do strong players rank appropriately higher?
  - Do upsets affect ratings realistically?
  - Does the rating distribution avoid collapsing or blowing up over time?

##### 2. Future-Proof Decoupling
By isolating SQL execution into a command processor, the input mechanism becomes fully swappable.

**Today:**
- The input mechanism is a text file (`input.txt`).

**Future (Flask/FastAPI):**
- Each line of `input.txt` can map directly to an HTTP route or JSON payload.
- The command loop already acts like a miniature request dispatcher.

This mirrors the structure of HTTP requests in concept (not in protocol):
- a verb (`POST`, `GET`) → command name,
- a payload → command arguments.

The transition to an API becomes trivial as the core logic remains unchanged. The only difference will be that instead of reading lines from a file, the system will read JSON from a web request.

##### 3. Maintainability Through External SQL Files
Storing queries in `.sql` files (instead of inline strings) provides clarity and maintainability:

- **Separation of Concerns:** Python handles logic while SQL handles data manipulation.
- **Syntax Highlighting & Tooling:** I can open or test queries directly in DBeaver (a SQL database visualization tool) without running the Python app.
- **Cleaner Git History:** Schema or query changes show up clearly without greatly impacting Python files.
- **Ease of Collaboration:** Queries become standalone modules instead of blobs buried in code.

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
* Product Adoption & Community Impact: Introduce the fully developed system for use by a live competitive gaming community. This will provide real-world performance metrics, concurrency data, and user feedback necessary to validate the architectural choices (Triggers, Indexes) and guide future feature development.

Contact & Contribution
* Author: Samuel Yoon
* Project Link: https://github.com/samuelyoon17/boiler_royale.git
