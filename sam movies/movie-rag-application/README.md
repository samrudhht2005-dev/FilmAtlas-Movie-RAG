
# Movie RAG Application

## Overview

A Retrieval-Augmented Generation (RAG) application that
answers movie-related questions using a Neo4j knowledge
graph and a large language model.

## Technologies

- Python
- Streamlit
- Neo4j
- Cypher
- LangChain
- OpenAI

## Features

- Search for movies, actors, and directors.
- Retrieve information from a graph database.
- Generate natural-language answers using an LLM.
- View the retrieved graph data.
- Check the database connection.

## Installation

Create and activate a virtual environment, then run:

```bash
pip install -r requirements.txt
```

## Configuration

Create a `.env` file with your Neo4j connection details
and OpenAI API key.

## Database Setup

Execute the queries in `database/schema.cypher`
in the Neo4j Query interface.

## Run the Application

```bash
streamlit run app.py
```

## Workflow

User Question → Query Classification → Neo4j Retrieval
→ Context Preparation → LLM Answer Generation
→ Answer Display
