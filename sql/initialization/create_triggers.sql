CREATE OR REPLACE FUNCTION update_elo_on_match_insert()
RETURNS TRIGGER AS $$
DECLARE
    p1_elo INTEGER;
    p2_elo INTEGER;

    expected_score NUMERIC;
    actual_score NUMERIC;

    K CONSTANT INTEGER := 32;
    DIVISOR CONSTANT NUMERIC := 400.0;
BEGIN
    SELECT elo INTO p1_elo FROM users WHERE player_tag = NEW.player1_tag;
    SELECT elo INTO p2_elo FROM users WHERE player_tag = NEW.player2_tag;

    IF NEW.winner_tag = NEW.player1_tag THEN
        actual_score := 1.0;
    ELSE
        actual_score := 0.0;
    END IF;

    expected_score := 1.0 / (1.0 + POWER(10.0, (p2_elo - p1_elo) / DIVISOR));

    UPDATE users
    SET elo = ROUND(p1_elo + K * (actual_score - expected_score))
    WHERE player_tag = NEW.player1_tag;

    UPDATE users
    SET elo = ROUND(p2_elo - K * (actual_score - expected_score))
    WHERE player_tag = NEW.player2_tag;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION update_wins_losses_on_match_insert()
RETURNS TRIGGER AS $$
DECLARE
    p1_wins INTEGER;
    p1_losses INTEGER;
    p2_wins INTEGER;
    p2_losses INTEGER;

BEGIN
    UPDATE users
    SET wins = wins + 1
    WHERE player_tag = NEW.winner_tag;

    UPDATE users
    SET losses = losses + 1
    WHERE player_tag = CASE
        WHEN NEW.winner_tag = NEW.player1_tag THEN NEW.player2_tag
        ELSE NEW.player1_tag
    END;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER update_elo
AFTER INSERT ON battles
FOR EACH ROW
EXECUTE FUNCTION update_elo_on_match_insert();



CREATE TRIGGER update_wins_losses
AFTER INSERT ON battles
FOR EACH ROW
EXECUTE FUNCTION update_wins_losses_on_match_insert();
