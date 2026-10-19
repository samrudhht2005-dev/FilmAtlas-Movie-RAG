
import re
from services.neo4j_connection import run_query


STOP_WORDS = {
    "who", "what", "where", "when", "which", "is", "was", "are",
    "were", "the", "a", "an", "in", "on", "of", "to", "for",
    "and", "me", "tell", "show", "please", "movie", "movies",
    "film", "films", "acted", "acting", "actor", "actors",
    "actress", "directed", "director", "directors", "by", "feature",
    "features", "starring", "starred", "cast"
}


def retrieve_information(question):
    """Retrieve matching movie, actor, and director data from Neo4j."""
    words = [
        word.lower()
        for word in re.findall(r"[a-zA-Z0-9]+", question)
        if word.lower() not in STOP_WORDS
    ]

    if not words:
        words = [word.lower() for word in re.findall(
            r"[a-zA-Z0-9]+", question
        )]

    query = """
    MATCH (p:Person)-[r]->(m:Movie)
    WHERE any(word IN $words WHERE
        toLower(m.title) CONTAINS word OR
        toLower(p.name) CONTAINS word
    )
    RETURN p.name AS person,
           type(r) AS relationship,
           m.title AS movie,
           m.released AS released
    ORDER BY movie, person
    """

    return run_query(query, {"words": words})


def generate_answer(question, context):
    """Create a readable answer using database results only."""
    if not context:
        return (
            "I couldn't find matching information in your movie database. "
            "Try a movie title, actor name, or director name."
        )

    q = question.lower()
    records = context if isinstance(context, list) else []

    if "director" in q or "directed" in q:
        selected = [
            row for row in records
            if row.get("relationship") == "DIRECTED"
        ]
        if selected:
            answers = []
            for row in selected:
                item = f"{row['person']} directed {row['movie']}"
                if item not in answers:
                    answers.append(item)
            return ". ".join(answers) + "."

    if any(word in q for word in ("actor", "actress", "acted", "cast",
                                   "starring", "starred", "feature")):
        selected = [
            row for row in records
            if row.get("relationship") == "ACTED_IN"
        ]
        if selected:
            answers = []
            for row in selected:
                item = f"{row['person']} acted in {row['movie']}"
                if item not in answers:
                    answers.append(item)
            return ". ".join(answers) + "."

    answers = []
    for row in records:
        relationship = row.get("relationship", "")
        person = row.get("person", "Unknown")
        movie = row.get("movie", "Unknown")
        released = row.get("released")

        if relationship == "DIRECTED":
            item = f"{person} directed {movie}"
        elif relationship == "ACTED_IN":
            item = f"{person} acted in {movie}"
        else:
            item = f"{person} is associated with {movie}"

        if released:
            item += f" ({released})"

        if item not in answers:
            answers.append(item)

    return ". ".join(answers) + "." if answers else (
        "I couldn't find a matching answer in the database."
    )

