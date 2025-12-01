BEGIN;

WITH players AS (
    SELECT
        p1.player_tag AS p1_tag,
        p2.player_tag AS p2_tag,
        p1.elo AS p1_elo,
        p2.elo AS p2_elo
    FROM users p1
    JOIN users p2
      ON p1.player_tag = %s
     AND p2.player_tag = %s
)

UPDATE users u
SET elo = CASE
    WHEN u.player_tag = p.p1_tag THEN p.p1_elo + 32 * (1 - (1 / (1 + POWER(10, (p.p2_elo - p.p1_elo) / 400.0))))
    WHEN u.player_tag = p.p2_tag THEN p.p2_elo + 32 * (0 - (1 / (1 + POWER(10, (p.p1_elo - p.p2_elo) / 400.0))))
END
FROM players p
WHERE u.player_tag IN (p.p1_tag, p.p2_tag);


COMMIT;
