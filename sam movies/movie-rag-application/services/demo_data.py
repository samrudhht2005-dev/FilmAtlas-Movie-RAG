import re

DEMO_MOVIES = [
    {
        "title": "Arrival",
        "released": 2016,
        "director": "Denis Villeneuve",
        "cast": ["Amy Adams", "Jeremy Renner", "Forest Whitaker"],
        "genre": "Sci-Fi, Mystery, Drama",
        "description": "A linguist works with the military to communicate with alien lifeforms after twelve mysterious spacecraft appear around the world.",
    },
    {
        "title": "Perfect Blue",
        "released": 1997,
        "director": "Satoshi Kon",
        "cast": ["Junko Iwao", "Rica Matsumoto", "Shinpachi Tsuji"],
        "genre": "Psychological Thriller, Anime, Mystery",
        "description": "A pop idol gives up her singing career to become an actress, only to be haunted by a stalker and hallucinations of her past self.",
    },
    {
        "title": "Andhadhun",
        "released": 2018,
        "director": "Sriram Raghavan",
        "cast": ["Ayushmann Khurrana", "Tabu", "Radhika Apte"],
        "genre": "Black Comedy, Crime, Thriller",
        "description": "A piano player pretending to be visually impaired unwittingly becomes entangled in the murder of a former film star.",
    },
    {
        "title": "The Lunchbox",
        "released": 2013,
        "director": "Ritesh Batra",
        "cast": ["Irrfan Khan", "Nimrat Kaur", "Nawazuddin Siddiqui"],
        "genre": "Romance, Drama",
        "description": "A mistaken delivery in Mumbai's famously efficient lunchbox delivery system connects a lonely widower with an unhappy housewife.",
    },
    {
        "title": "Train to Busan",
        "released": 2016,
        "director": "Yeon Sang-ho",
        "cast": ["Gong Yoo", "Jung Yu-mi", "Ma Dong-seok"],
        "genre": "Action, Horror, Thriller",
        "description": "As a zombie virus breaks out in South Korea, passengers struggle to survive on a high-speed bullet train from Seoul to Busan.",
    },
]


def get_demo_movie_count():
    return len(DEMO_MOVIES)


def get_demo_recent_movies(limit=12):
    sorted_movies = sorted(DEMO_MOVIES, key=lambda m: m["released"], reverse=True)
    return sorted_movies[:limit]


def search_demo_movies(question):
    """Search demo movies and return graph records and matched movies."""
    q = question.lower()
    words = [w for w in re.findall(r"[a-zA-Z0-9]+", q) if len(w) > 2]

    matched_movies = []
    records = []

    for m in DEMO_MOVIES:
        title_lower = m["title"].lower()
        director_lower = m["director"].lower()
        cast_lower = [c.lower() for c in m["cast"]]
        genre_lower = m["genre"].lower()
        desc_lower = m["description"].lower()

        title_match = title_lower in q or any(w in title_lower for w in words)
        director_match = director_lower in q or any(w in director_lower for w in words)
        actor_match = any(c in q or any(w in c for w in words) for c in cast_lower)
        genre_match = any(w in genre_lower for w in words)
        desc_match = any(w in desc_lower for w in words)

        if title_match or director_match or actor_match or genre_match or desc_match:
            matched_movies.append(m)
            records.append({
                "person": m["director"],
                "relationship": "DIRECTED",
                "movie": m["title"],
                "released": m["released"],
                "genre": m["genre"],
                "description": m["description"],
            })
            for actor in m["cast"]:
                records.append({
                    "person": actor,
                    "relationship": "ACTED_IN",
                    "movie": m["title"],
                    "released": m["released"],
                    "genre": m["genre"],
                    "description": m["description"],
                })

    if not matched_movies and any(k in q for k in ["movie", "movies", "film", "films", "all", "list", "show", "recommend"]):
        matched_movies = DEMO_MOVIES
        for m in DEMO_MOVIES:
            records.append({
                "person": m["director"],
                "relationship": "DIRECTED",
                "movie": m["title"],
                "released": m["released"],
                "genre": m["genre"],
                "description": m["description"],
            })

    return records, matched_movies


def generate_demo_answer(question, records, matched_movies):
    """Generate a clean, informative answer from the local sample data."""
    if not matched_movies:
        return (
            "I couldn't find matching information in the local sample movie database. "
            "Try searching for movies like Arrival, Perfect Blue, Andhadhun, The Lunchbox, or Train to Busan."
        )

    q = question.lower()

    if "director" in q or "directed" in q or "who directed" in q:
        parts = [f"{m['title']} ({m['released']}) was directed by {m['director']}." for m in matched_movies]
        return " ".join(parts)

    if any(k in q for k in ["actor", "actors", "actress", "cast", "star", "stars", "who acted"]):
        parts = [f"{m['title']} ({m['released']}) stars {', '.join(m['cast'])}." for m in matched_movies]
        return " ".join(parts)

    if any(k in q for k in ["genre", "genres", "type"]):
        parts = [f"{m['title']} belongs to the {m['genre']} genre." for m in matched_movies]
        return " ".join(parts)

    if any(k in q for k in ["about", "plot", "story", "synopsis", "what is"]):
        parts = [f"{m['title']} ({m['released']}): {m['description']} (Directed by {m['director']}; Genre: {m['genre']})" for m in matched_movies]
        return "\n\n".join(parts)

    # General overview
    parts = []
    for m in matched_movies:
        parts.append(
            f"🎬 **{m['title']}** ({m['released']})\n\n"
            f"• **Director:** {m['director']}\n"
            f"• **Cast:** {', '.join(m['cast'])}\n"
            f"• **Genre:** {m['genre']}\n"
            f"• **Overview:** {m['description']}"
        )
    return "\n\n".join(parts)
