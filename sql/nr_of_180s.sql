-- Query for nr of 180s
SELECT STRFTIME("%Y-%m-%d", games.game_start) AS date, 
       COUNT(throws.sum) AS visits_180
FROM games
JOIN throws ON games.game_id=throws.game_id
WHERE throw_1='T20' AND throw_2='T20' AND throw_3='T20'
GROUP BY date;
