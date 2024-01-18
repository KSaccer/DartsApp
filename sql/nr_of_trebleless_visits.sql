-- Query for nr of trebleless visits
SELECT STRFTIME("%Y-%m-%d", games.game_start) AS date, 
       SUM(CASE 
              WHEN throw_1 NOT LIKE 'T%' AND throw_2 NOT LIKE 'T%' AND throw_3 NOT LIKE 'T%'
              THEN 1 
              ELSE 0
       END) AS trebleless,
       COUNT(throws.sum) AS visits
FROM games
JOIN throws ON games.game_id=throws.game_id
GROUP BY date;
