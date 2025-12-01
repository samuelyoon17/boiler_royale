SELECT DISTINCT clash_royale_name, player_tag, username, elo
FROM users
INNER JOIN battles ON (users.player_tag = battles.player1_tag OR users.player_tag = battles.player2_tag )
WHERE battles.tournament_id = %s
ORDER BY elo DESC;
