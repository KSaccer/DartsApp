-- Creating tables for games
CREATE TABLE IF NOT EXISTS games (
    game_id INT,
    datetime DATETIME,
    type TEXT NOT NULL,
    PRIMARY KEY (game_id)
    );

-- Creating tables for throws
CREATE TABLE IF NOT EXISTS throws (
    game_id INT,
    timestamp TIMESTAMP NOT NULL,
    throw_1 TEXT NOT NULL,
    throw_2 TEXT NOT NULL,
    throw_3 TEXT NOT NULL,
    PRIMARY KEY(timestamp),
    FOREIGN KEY(game_id) REFERENCES games(game_id)
    );