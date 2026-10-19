
MOVIE_QUERY = """
MATCH (m:Movie)
WHERE toLower(m.title) CONTAINS toLower($keyword)
OPTIONAL MATCH (m)<-[:ACTED_IN]-(a:Person)
OPTIONAL MATCH (m)<-[:DIRECTED]-(d:Person)
RETURN m.title AS movie,
       m.released AS released,
       collect(DISTINCT a.name) AS actors,
       collect(DISTINCT d.name) AS directors
LIMIT 10
"""

ACTOR_QUERY = """
MATCH (p:Person)-[:ACTED_IN]->(m:Movie)
WHERE toLower(p.name) CONTAINS toLower($keyword)
RETURN p.name AS actor,
       collect(DISTINCT m.title) AS movies
LIMIT 10
"""

DIRECTOR_QUERY = """
MATCH (p:Person)-[:DIRECTED]->(m:Movie)
WHERE toLower(p.name) CONTAINS toLower($keyword)
RETURN p.name AS director,
       collect(DISTINCT m.title) AS movies
LIMIT 10
"""

GENERAL_QUERY = """
MATCH (m:Movie)
OPTIONAL MATCH (m)<-[:ACTED_IN]-(a:Person)
OPTIONAL MATCH (m)<-[:DIRECTED]-(d:Person)
RETURN m.title AS movie,
       collect(DISTINCT a.name) AS actors,
       collect(DISTINCT d.name) AS directors
ORDER BY movie
LIMIT 30
"""
