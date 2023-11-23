-- Query for number of games
SELECT STRFTIME("%Y-%m-%d", games.game_start) AS date, 
       COUNT(games.game_id) AS nr_of_games
FROM games
GROUP BY date;
