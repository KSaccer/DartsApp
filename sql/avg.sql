-- Query for 3-dart-average
SELECT STRFTIME("%Y-%m-%d", games.game_start) AS date, 
       SUM(throws.sum) AS overall_score,
       COUNT(throws.sum) AS visits
FROM games
JOIN throws ON games.game_id=throws.game_id
GROUP BY date;
