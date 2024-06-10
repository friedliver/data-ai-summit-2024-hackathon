import streamlit as st
import string
import random
import os
from dotenv import load_dotenv

from databricks import vector_search
from databricks_genai_inference import ChatCompletion, Embedding
from neo4j import GraphDatabase

# Load environment variables from .env file
load_dotenv()

NEO4J_PROTOCOL = os.getenv("NEO4J_PROTOCOL")
NEO4J_CONNECTION_URL = os.getenv("NEO4J_CONNECTION_URL")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

def random_string() -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=10))

def chat_actions():
    # Add user input to chat history
    st.session_state["chat_history"].append(
        {"role": "user", "content": st.session_state["chat_input"]},
    )

    # Embed user input
    embeded_input = Embedding.create(
        model="bge-large-en",
        input="3D ActionSLAM: wearable person tracking in multi-floor environments")[0]

    # Vector search with user input
    client = vector_search.VectorSearchClient()

    results = client.similarity_search(
        index_name="speakers_index",  # Replace with your actual index name
        query_vector=embeded_input,  # Replace with your actual query vector
        num_results=5  # Number of results to return
    )

    for result in results:
        print(result)

    # # Generate cipher query
    # cipher_query = ""

    # # Fetch data from neo4j
    # with GraphDatabase.driver(f"{NEO4J_PROTOCOL}{NEO4J_CONNECTION_URL}", auth=(NEO4J_USER, NEO4J_PASSWORD)) as driver:
    #     records,_,_ = driver.execute_query(cipher_query, database_="neo4j")
    #     for record in records:
    #         print(record)

    # Build context/prompt

    response = ChatCompletion.create(model="databricks-meta-llama-3-70b-instruct",
                                    messages=[{"role": "system", "content": "You are a helpful assistant."},
                                            {"role": "user","content": st.session_state["chat_input"]}],
                                    max_tokens=128)

    # Write response to chat history
    st.session_state["chat_history"].append(
        {
            "role": "assistant",
            "content": response,
        },  # This can be replaced with your chat response logic
    )

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

st.chat_input("Enter your message", on_submit=chat_actions, key="chat_input")

for i in st.session_state["chat_history"]:
    with st.chat_message(name=i["role"]):
        st.write(i["content"])
