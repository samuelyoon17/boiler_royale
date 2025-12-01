CREATE TABLE users (
    player_tag VARCHAR(9) PRIMARY KEY,
    clash_royale_name VARCHAR(100) NOT NULL,
    username VARCHAR(100) NOT NULL,
    password_hash VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    firstname VARCHAR(50) NOT NULL,
    lastname VARCHAR(50) NOT NULL,
    elo INT DEFAULT 1200,
    wins INT DEFAULT 0,
    losses INT DEFAULT 0,
    years_played INT DEFAULT 0,
    date_joined TIMESTAMP DEFAULT NOW()
);

CREATE TABLE tournament (
    tournament_id SERIAL PRIMARY KEY,
    tournament_name VARCHAR(100) NOT NULL,
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP NOT NULL
);

CREATE TABLE battles (
    battle_id SERIAL PRIMARY KEY,
    tournament_id INT REFERENCES tournament (tournament_id),
    round_number INT NOT NULL,
    player1_tag VARCHAR(9) NOT NULL REFERENCES users (player_tag),
    player2_tag VARCHAR(9) NOT NULL REFERENCES users (player_tag),
    winner_tag VARCHAR(9) NOT NULL,
    match_result VARCHAR(3) NOT NULL,
    -- Format will be {crowns won by player 1}-{crowns won by player 2}
    -- Ex: 3-1 Player 1 defeats Player 2; 1-1 Player 1 ties with Player_2
    battle_date_time TIMESTAMP
);


CREATE INDEX idx_tournament_id ON battles (tournament_id);
CREATE INDEX idx_player1_tag ON battles (player1_tag);
CREATE INDEX idx_player2_tag ON battles (player2_tag);

CREATE INDEX idx_clash_royale_name ON users (clash_royale_name);
CREATE INDEX idx_username ON users (username);
