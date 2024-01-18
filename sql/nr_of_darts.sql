-- Query for number of darts thrown
SELECT STRFTIME("%Y-%m-%d", games.game_start) AS date, 
       COUNT(throws.sum) * 3 AS darts_thrown
FROM games
JOIN throws ON games.game_id=throws.game_id
GROUP BY date;