
import streamlit as st
from services.neo4j_connection import verify_connection, run_query
from services.rag_pipeline import retrieve_information, generate_answer
from services.demo_data import (
    DEMO_MOVIES,
    get_demo_movie_count,
    get_demo_recent_movies,
    search_demo_movies,
    generate_demo_answer,
)

st.set_page_config(
    page_title="CineVerse | Movie RAG",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------- CINEMATIC STYLING --------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');

.stApp {
    background: #08090d;
    color: #f5f5f5;
    font-family: 'DM Sans', sans-serif;
}

.block-container {
    max-width: 1250px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}

header[data-testid="stHeader"] {
    background: transparent;
}

section[data-testid="stSidebar"] {
    background: #101117;
    border-right: 1px solid #292a34;
}

h1, h2, h3, h4 {
    font-family: 'Playfair Display', serif !important;
    color: #ffffff !important;
}

.hero {
    padding: 42px 35px;
    border: 1px solid #34303a;
    border-radius: 22px;
    background:
        radial-gradient(ellipse at 85% 15%, #6f171b55, transparent 40%),
        linear-gradient(135deg, #191017, #0c0d13 65%);
    margin-bottom: 30px;
}

.eyebrow {
    color: #ff666d;
    letter-spacing: 4px;
    font-size: 12px;
    font-weight: 700;
    margin-bottom: 14px;
}

.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: clamp(38px, 6vw, 66px);
    line-height: 1.1;
    font-weight: 700;
    margin-bottom: 15px;
}

.hero-description {
    color: #b9bac5;
    font-size: 16px;
    max-width: 650px;
    line-height: 1.8;
}

.badge-demo {
    display: inline-block;
    background: rgba(230, 56, 66, 0.15);
    border: 1px solid #ff4c55;
    color: #ff737a;
    padding: 5px 14px;
    border-radius: 20px;
    font-size: 11px;
    letter-spacing: 2px;
    font-weight: 700;
    margin-bottom: 14px;
}

div[data-testid="stForm"] {
    background: #12131a;
    border: 1px solid #34303a;
    padding: 20px;
    border-radius: 16px;
}

.stTextInput input {
    background: #090a0f !important;
    color: white !important;
    border: 1px solid #3b3b48 !important;
    border-radius: 10px !important;
    min-height: 48px;
}

.stTextInput input:focus {
    border-color: #f0444c !important;
    box-shadow: 0 0 0 1px #f0444c !important;
}

.stButton button,
.stFormSubmitButton button {
    background: #e63842 !important;
    color: white !important;
    border: 1px solid #e63842 !important;
    border-radius: 10px !important;
    min-height: 44px;
    font-weight: 600;
    transition: all 0.2s ease;
}

.stButton button:hover,
.stFormSubmitButton button:hover {
    background: #ff4c55 !important;
    border-color: #ff4c55 !important;
}

.section-label {
    color: #ff666d;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 3px;
    margin-bottom: 8px;
}

.movie-card {
    min-height: 180px;
    background: linear-gradient(145deg, #191a24, #101117);
    border: 1px solid #30313c;
    border-radius: 15px;
    padding: 20px;
    margin-bottom: 16px;
    transition: transform 0.2s ease, border-color 0.2s ease;
}

.movie-card:hover {
    border-color: #ff666d55;
    transform: translateY(-2px);
}

.movie-title {
    font-family: 'Playfair Display', serif;
    font-size: 20px;
    font-weight: 700;
    margin-bottom: 6px;
    color: #ffffff;
}

.movie-year {
    color: #ff737a;
    font-size: 13px;
    font-weight: 600;
    margin-bottom: 6px;
}

.movie-genre {
    color: #c4c5d6;
    font-size: 12px;
    font-weight: 500;
    margin-bottom: 8px;
}

.movie-desc {
    color: #9d9eaec0;
    font-size: 13px;
    line-height: 1.6;
    margin-top: 6px;
}

.movie-crew {
    color: #ff666d;
    font-size: 12px;
    margin-top: 8px;
}

.answer-box {
    background: #13141c;
    border: 1px solid #38303a;
    border-left: 4px solid #ed414a;
    border-radius: 12px;
    padding: 22px;
    line-height: 1.8;
    color: #eeeeF3;
    margin: 15px 0;
    overflow-wrap: anywhere;
}

div[data-testid="stMetric"] {
    background: #13141c;
    border: 1px solid #30313c;
    border-radius: 13px;
    padding: 17px;
}

div[data-testid="stMetricValue"] {
    color: #ff666d;
}

hr {
    border-color: #292a34;
}

footer {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)


# -------------------- DATABASE & DEMO HELPERS --------------------

def is_demo_mode_active():
    return st.session_state.get("use_demo_mode", True)


def get_movie_count():
    if is_demo_mode_active():
        return get_demo_movie_count()
    try:
        result = run_query("MATCH (m:Movie) RETURN count(m) AS total")
        return result[0]["total"] if result else 0
    except Exception:
        return get_demo_movie_count()


def get_recent_movies(limit=12):
    if is_demo_mode_active():
        return get_demo_recent_movies(limit)
    try:
        query = """
        MATCH (m:Movie)
        RETURN m.title AS title, m.released AS released
        ORDER BY m.released DESC, m.title
        LIMIT $limit
        """
        results = run_query(query, {"limit": limit})
        return results if results else get_demo_recent_movies(limit)
    except Exception:
        return get_demo_recent_movies(limit)


def ask_movie_question(question):
    with st.spinner("Searching your movie universe..."):
        try:
            if is_demo_mode_active():
                records, matched = search_demo_movies(question)
                answer = generate_demo_answer(question, records, matched)
                st.session_state["movie_question"] = question
                st.session_state["movie_answer"] = answer
                st.session_state["movie_context"] = records
                st.session_state["matched_demo_movies"] = matched
            else:
                context = retrieve_information(question)
                answer = generate_answer(question, context)
                st.session_state["movie_question"] = question
                st.session_state["movie_answer"] = answer
                st.session_state["movie_context"] = context
                st.session_state.pop("matched_demo_movies", None)
        except Exception:
            # Fall back gracefully to local demo data
            records, matched = search_demo_movies(question)
            answer = generate_demo_answer(question, records, matched)
            st.session_state["movie_question"] = question
            st.session_state["movie_answer"] = answer
            st.session_state["movie_context"] = records
            st.session_state["matched_demo_movies"] = matched


# -------------------- SIDEBAR --------------------

with st.sidebar:
    st.markdown("## 🎬 CINEVERSE")
    st.caption("YOUR PERSONAL MOVIE KNOWLEDGE GRAPH")
    st.divider()

    st.markdown("### Navigation")
    st.markdown("🔎  Movie intelligence")
    st.markdown("🎞️  Movie collection")

    st.divider()
    st.markdown("### Database Status")

    if st.session_state.get("neo4j_connected", False):
        st.success("🟢 Neo4j Aura: Connected")
    else:
        st.caption("🔴 Neo4j Aura: Offline")

    use_demo = st.toggle(
        "Local Demo Mode",
        value=st.session_state.get("use_demo_mode", True),
        help="Use local curated sample movies (Arrival, Perfect Blue, Andhadhun, The Lunchbox, Train to Busan)",
    )
    st.session_state["use_demo_mode"] = use_demo

    if st.button("Test Neo4j connection", use_container_width=True):
        try:
            result = verify_connection()
            if isinstance(result, tuple):
                connected = result[0]
                message = result[1] if len(result) > 1 else ""
            else:
                connected = bool(result)
                message = ""
            st.session_state["neo4j_connected"] = connected
            if connected:
                st.success(message or "Neo4j connected successfully!")
                st.session_state["use_demo_mode"] = False
            else:
                st.error(message or "Connection failed.")
        except Exception as error:
            st.session_state["neo4j_connected"] = False
            st.error(f"Connection failed: {error}")

    st.caption("Powered by Neo4j and Streamlit")


# -------------------- HERO --------------------

demo_badge_html = ""
if is_demo_mode_active():
    demo_badge_html = '<div class="badge-demo">⚡ LOCAL DEMO MODE</div>'

st.markdown(f"""
<div class="hero">
    {demo_badge_html}
    <div class="eyebrow">YOUR CINEMATIC UNIVERSE</div>
    <div class="hero-title">Every movie has<br> a story to connect.</div>
    <div class="hero-description">
        Explore movies, discover directors and actors, and ask questions
        about your movie knowledge graph in one place.
    </div>
</div>
""", unsafe_allow_html=True)


# -------------------- SEARCH --------------------

st.markdown('<div class="section-label">MOVIE INTELLIGENCE</div>',
            unsafe_allow_html=True)
st.subheader("What would you like to discover?")

with st.form("movie_search_form"):
    question = st.text_input(
        "Ask a question",
        placeholder="e.g. Who directed Arrival? or Tell me about Andhadhun",
        label_visibility="collapsed",
    )
    submitted = st.form_submit_button(
        "Search the universe  →",
        use_container_width=True,
    )

if submitted and question.strip():
    ask_movie_question(question.strip())

if "movie_answer" in st.session_state:
    st.markdown("### Your answer")
    st.markdown(
        '<div class="answer-box">' +
        str(st.session_state["movie_answer"]).replace("\n", "<br>") +
        '</div>',
        unsafe_allow_html=True,
    )

    matched_results = st.session_state.get("matched_demo_movies", [])
    if matched_results:
        st.markdown("#### Matched Movies")
        cols = st.columns(min(len(matched_results), 3))
        for idx, m in enumerate(matched_results):
            with cols[idx % len(cols)]:
                genre_html = f'<div class="movie-genre">{m.get("genre", "")}</div>' if m.get("genre") else ""
                desc_html = f'<div class="movie-desc">{m.get("description", "")}</div>' if m.get("description") else ""
                st.markdown(
                    f"""
                    <div class="movie-card">
                        <div class="section-label">MATCH #{idx+1}</div>
                        <div class="movie-title">{m['title']}</div>
                        <div class="movie-year">{m.get('released', '')} · Dir: {m.get('director', 'Unknown')}</div>
                        {genre_html}
                        {desc_html}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    if st.button("Clear answer"):
        for key in ("movie_question", "movie_answer", "movie_context", "matched_demo_movies"):
            st.session_state.pop(key, None)
        st.rerun()


# -------------------- COLLECTION OVERVIEW --------------------

st.divider()
st.markdown('<div class="section-label">THE DATABASE</div>',
            unsafe_allow_html=True)
st.header("Inside your movie universe")

count_col, info_col = st.columns([1, 2])

with count_col:
    st.metric("Movies in your graph", get_movie_count())

with info_col:
    if is_demo_mode_active():
        st.markdown("""
        **Local Demo Mode Active**: Displaying curated sample films connecting titles, directors, cast members, and story synopsis across diverse genres.
        """)
    else:
        st.markdown("""
        Your collection connects movie titles with directors and cast members.
        Search for a movie, find who directed it, or discover which movies
        share an actor.
        """)


# -------------------- MOVIE COLLECTION --------------------

st.markdown("### Recently released movies")

try:
    movies = get_recent_movies()

    if movies:
        columns = st.columns(3)

        for index, movie in enumerate(movies):
            with columns[index % 3]:
                title = movie.get("title") or "Untitled"
                year = movie.get("released") or "Year unknown"
                genre = movie.get("genre", "")
                desc = movie.get("description", "")
                director = movie.get("director", "")
                cast = movie.get("cast", [])

                genre_html = f'<div class="movie-genre">{genre}</div>' if genre else ""
                desc_html = f'<div class="movie-desc">{desc}</div>' if desc else ""
                crew_html = ""
                if director or cast:
                    crew_parts = []
                    if director:
                        crew_parts.append(f"Dir: {director}")
                    if cast:
                        crew_parts.append(f"Stars: {', '.join(cast[:2])}")
                    crew_html = f'<div class="movie-crew">{" · ".join(crew_parts)}</div>'

                st.markdown(
                    f"""
                    <div class="movie-card">
                        <div class="section-label">MOVIE COLLECTION</div>
                        <div class="movie-title">{title}</div>
                        <div class="movie-year">{year}</div>
                        {genre_html}
                        {desc_html}
                        {crew_html}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
    else:
        st.info("No movies found. Add movie data to your Neo4j database.")

except Exception as error:
    st.warning("Couldn't load the movie collection. Check your Neo4j connection.")
    st.caption(str(error))


# -------------------- FOOTER --------------------

st.divider()
st.caption("CINEVERSE · A Movie RAG Experience")

