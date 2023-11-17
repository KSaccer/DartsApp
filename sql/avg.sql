-- Query for monthly 3-dart-average
SELECT STRFTIME("%Y-%m", games.game_start) AS month, 
       ROUND(CAST(SUM(throws.sum) AS float) / COUNT(throws.sum), 1) AS average     
FROM games
JOIN throws ON games.game_id=throws.game_id
GROUP BY month;
