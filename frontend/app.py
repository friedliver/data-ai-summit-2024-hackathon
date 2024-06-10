import streamlit as st
import string
import random
import os
from dotenv import load_dotenv

from databricks.vector_search.client import VectorSearchClient
from databricks_genai_inference import ChatCompletion, Embedding
from neo4j import GraphDatabase

# Load environment variables from .env file
load_dotenv()

NEO4J_PROTOCOL = os.getenv("NEO4J_PROTOCOL")
NEO4J_CONNECTION_URL = os.getenv("NEO4J_CONNECTION_URL")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")


def generate_cypher_prompt(question: str, schema: str) -> str:
    """
    Generate a prompt to translate a natural language question into a Cypher query.
 
    Args:
        question: The natural language question to be translated.
        schema: The schema information of the graph database.
 
    Returns:
        A prompt string to be used for generating the Cypher query.
    """
    prompt = f"""
    You are a Neo4j expert. Given an input question, create a syntactically correct Cypher query to run.
 
    Here is the schema information:
    {schema}
 
    Below are a number of examples of questions and their corresponding Cypher queries.
 
    User input: How many speakers are there?
    Cypher query: MATCH (s:Speaker) RETURN count(DISTINCT s)
 
    User input: Which speakers are presenting in the session titled 'Simplify GenAI App Development with Secure, Custom AI Agents'?
    Cypher query: MATCH (s:Session {{title: 'Simplify GenAI App Development with Secure, Custom AI Agents'}})<-[:SPEAKS_AT]-(sp:Speaker) RETURN sp.name
 
    User input: How many sessions is Aakrati Talati speaking at?
    Cypher query: MATCH (sp:Speaker {{name: 'Aakrati Talati'}})-[:SPEAKS_AT]->(s:Session) RETURN count(s)
 
    User input: List all the categories of the session titled 'The AI Regulatory Landscape: What’s Here? What’s Coming? How to Prepare?'
    Cypher query: MATCH (s:Session {{title: 'The AI Regulatory Landscape: What’s Here? What’s Coming? How to Prepare?'}})-[:BELONGS_TO_CATEGORY]->(c:Category) RETURN c.name
 
    User input: Which speakers are involved in sessions from both the 'Generative AI' and 'Data Governance' tracks?
    Cypher query: MATCH (sp:Speaker)-[:SPEAKS_AT]->(s1:Session)-[:BELONGS_TO_TRACK]->(t1:Track {{name: 'Generative AI'}})
                  MATCH (sp)-[:SPEAKS_AT]->(s2:Session)-[:BELONGS_TO_TRACK]->(t2:Track {{name: 'Data Governance'}})
                  RETURN sp.name
 
    User input: {question}
    Cypher query:
    """
    return prompt

def generate_response_prompt(question: str, context: str) -> str:
    """
    Generate a prompt to synthesize a response to the user's natural language query using the context retrieved from the vector database.
 
    Args:
        question: The natural language question posed by the user.
        context: The context information retrieved from the vector database.
 
    Returns:
        A prompt string to be used for generating the response.
    """
    prompt = f"""
    You are an AI assistant with expertise in the Data + AI Summit 2024 by Databricks. Given an input question, use the provided context to generate a comprehensive and accurate response.
 
    Here is the context information retrieved from the vector database:
    {context}
 
    Below are a number of examples of questions and their corresponding responses based on the context.
 
    User input: Who are the speakers for the session titled 'Simplify GenAI App Development with Secure, Custom AI Agents'?
    Context: The session 'Simplify GenAI App Development with Secure, Custom AI Agents' is presented by Aakrati Talati.
    Response: The speakers for the session titled 'Simplify GenAI App Development with Secure, Custom AI Agents' include Aakrati Talati.
 
    User input: What topics will be covered in the session 'The AI Regulatory Landscape: What’s Here? What’s Coming? How to Prepare?'?
    Context: The session 'The AI Regulatory Landscape: What’s Here? What’s Coming? How to Prepare?' covers topics such as AI/Machine Learning, GenAI/LLMs, and Data Governance.
    Response: The session 'The AI Regulatory Landscape: What’s Here? What’s Coming? How to Prepare?' will cover topics including AI/Machine Learning, GenAI/LLMs, and Data Governance.
 
    User input: Which companies are represented by speakers in the 'Generative AI' track?
    Context: The 'Generative AI' track includes speakers from companies such as Databricks and OpenAI.
    Response: The companies represented by speakers in the 'Generative AI' track include Databricks and OpenAI.
 
    User input: {question}
    Response:
    """
    return prompt

def chat_actions():
    # Add user input to chat history
    st.session_state["chat_history"].append(
        {"role": "user", "content": st.session_state["chat_input"]},
    )

    # Embed user input
    embeded_input = Embedding.create(
        model="bge-large-en",
        input="3D ActionSLAM: wearable person tracking in multi-floor environments")

    # Vector search with user input
    vsc = VectorSearchClient()
    index = vsc.get_index(endpoint_name="vs_endpoint", index_name="workspace.default.speakers_index")

    results = index.similarity_search(
        columns=["Embeddings"],
        query_vector=embeded_input.embeddings[0],  # Replace with your actual query vector
    )

    print(results)

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
