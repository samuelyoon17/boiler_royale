SELECT
    clash_royale_name,
    player_tag,
    username,
    elo,
    COALESCE(SUM(CASE WHEN b.winner_tag = u.player_tag THEN 1 ELSE 0 END), 0) AS tournament_wins,
    COALESCE(SUM(CASE WHEN b.winner_tag != u.player_tag THEN 1 ELSE 0 END), 0) AS tournament_losses
FROM users u
LEFT JOIN battles b
ON u.player_tag in (b.player1_tag, b.player2_tag) AND b.tournament_id = %s
WHERE u.player_tag = %s
GROUP BY
    u.clash_royale_name,
    u.player_tag,
    u.username,
    u.elo;
