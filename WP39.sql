SELECT match_id, count(killer_name) AS suicide_count
FROM match_frag
WHERE victim_name is NULL
GROUP BY match_id
ORDER BY suicide_count;