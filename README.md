Archive

Development process for update_elo.sql

Originally had multiple update commands but felt very repetitive

Researched how to update mutliple rows and learned about CTE, CASE, and WHERE u.player_tag IN (p.p1_tag, p.p2_tag);

Through some conversations with Gemini, I learned how these functioned, attempted with my code, and asked Gemini for debugging help



Triggers
After developing the update_elo.sql in archive, I learned about triggers and how they improve atomicity.

Including online articles, I used Gemini to help me learn how to reference columns from battle insertions and that I should put my commands and function into the same sql initalization file



get_user_tournament_info
used LEFT JOIN and tournament_id in ON clause to ensure something is alwaysr returned
