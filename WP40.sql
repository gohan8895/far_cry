SELECT killer_name AS player_name, count(killer_name) AS kill_count
FROM match_frag
GROUP BY killer_name
ORDER BY kill_count DESC, killer_name;