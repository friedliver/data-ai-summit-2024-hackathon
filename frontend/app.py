import streamlit as st
import os

from databricks.vector_search.client import VectorSearchClient
from databricks_genai_inference import ChatCompletion, Embedding
from neo4j import GraphDatabase

NEO4J_PROTOCOL = os.getenv("NEO4J_PROTOCOL")
NEO4J_CONNECTION_URL = os.getenv("NEO4J_CONNECTION_URL")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

neo4j_schema = "Schema Information: Speaker nodes have properties: name, bio, company, job_title Company nodes have a property: name JobTitle nodes have a property: title Session nodes have properties: title, id, duration, alias Type, Level, Category, Track, and Delivery nodes have a property: name Relationships: (:Speaker)-[:WORKS_FOR]->(:Company) (:Speaker)-[:HAS_JOB_TITLE]->(:JobTitle) (:Speaker)-[:SPEAKS_AT]->(:Session) (:Session)-[:HAS_TYPE]->(:Type) (:Session)-[:HAS_LEVEL]->(:Level) (:Session)-[:BELONGS_TO_CATEGORY]->(:Category) (:Session)-[:BELONGS_TO_TRACK]->(:Track) (:Session)-[:HAS_DELIVERY]->(:Delivery)"

def generate_cypher_prompt(question: str, schema: str, context: str) -> str:
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
    Cypher query: MATCH (s:Speaker)
                  OPTIONAL MATCH (s)-[:RELATED_TO]->(related:Person)
                  OPTIONAL MATCH (s)-[:RELATED_TO]->(related:Talk)
                  RETURN count(DISTINCT s), collect(DISTINCT related)
    User input: Which speakers are presenting in the session titled 'Simplify GenAI App Development with Secure, Custom AI Agents'?
    Cypher query: MATCH (s:Session {{title: 'Simplify GenAI App Development with Secure, Custom AI Agents'}})<-[:SPEAKS_AT]-(sp:Speaker)
                  OPTIONAL MATCH (sp)-[:RELATED_TO]->(related:Person)
                  OPTIONAL MATCH (sp)-[:RELATED_TO]->(related:Talk)
                  RETURN sp.name, collect(DISTINCT related)
    User input: How many sessions is Aakrati Talati speaking at?
    Cypher query: MATCH (sp:Speaker {{name: 'Aakrati Talati'}})-[:SPEAKS_AT]->(s:Session)
                  OPTIONAL MATCH (sp)-[:RELATED_TO]->(related:Person)
                  OPTIONAL MATCH (sp)-[:RELATED_TO]->(related:Talk)
                  RETURN count(s), collect(DISTINCT related)
    User input: List all the categories of the session titled 'The AI Regulatory Landscape: What’s Here? What’s Coming? How to Prepare?'
    Cypher query: MATCH (s:Session {{title: 'The AI Regulatory Landscape: What’s Here? What’s Coming? How to Prepare?'}})-[:BELONGS_TO_CATEGORY]->(c:Category)
                  OPTIONAL MATCH (s)-[:RELATED_TO]->(related:Person)
                  OPTIONAL MATCH (s)-[:RELATED_TO]->(related:Talk)
                  RETURN c.name, collect(DISTINCT related)
    User input: Which speakers are involved in sessions from both the 'Generative AI' and 'Data Governance' tracks?
    Cypher query: MATCH (sp:Speaker)-[:SPEAKS_AT]->(s1:Session)-[:BELONGS_TO_TRACK]->(t1:Track {{name: 'Generative AI'}})
                  MATCH (sp)-[:SPEAKS_AT]->(s2:Session)-[:BELONGS_TO_TRACK]->(t2:Track {{name: 'Data Governance'}})
                  OPTIONAL MATCH (sp)-[:RELATED_TO]->(related:Person)
                  OPTIONAL MATCH (sp)-[:RELATED_TO]->(related:Talk)
                  RETURN sp.name, collect(DISTINCT related)
    User input: {question}
    Context: {context}
    Cypher query:

    EMIT ONLY CODE WITHOUT ANY FORMATTING
    """
    return prompt

def generate_query_context_prompt(question: str, context: str) -> str:
    """
    Generate a prompt to synthesize a response to the user"s natural language query using the context retrieved from the vector database.
 
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
 
    User input: Who are the speakers for the session titled "Simplify GenAI App Development with Secure, Custom AI Agents"?
    Context: The session "Simplify GenAI App Development with Secure, Custom AI Agents" is presented by Aakrati Talati.
    Response: The speakers for the session titled "Simplify GenAI App Development with Secure, Custom AI Agents" include Aakrati Talati.
 
    User input: What topics will be covered in the session "The AI Regulatory Landscape: What’s Here? What’s Coming? How to Prepare?"?
    Context: The session "The AI Regulatory Landscape: What’s Here? What’s Coming? How to Prepare?" covers topics such as AI/Machine Learning, GenAI/LLMs, and Data Governance.
    Response: The session "The AI Regulatory Landscape: What’s Here? What’s Coming? How to Prepare?" will cover topics including AI/Machine Learning, GenAI/LLMs, and Data Governance.
 
    User input: Which companies are represented by speakers in the "Generative AI" track?
    Context: The "Generative AI" track includes speakers from companies such as Databricks and OpenAI.
    Response: The companies represented by speakers in the "Generative AI" track include Databricks and OpenAI.
 
    User input: {question}
    Response:
    """
    return prompt

def generate_response_prompt(question: str, query_results: str) -> str:
    """
    Generate a prompt to synthesize a final response based on the results of a Neo4j query.
    Args:
        question: The natural language question asked by the user.
        query_results: The results of the Neo4j query in a structured format (e.g., JSON).
    Returns:
        A prompt string to be used for generating the final response.
    """
    prompt = f"""
    You are an AI assistant. Given an input question and the results of a Neo4j query, synthesize a final response to answer the user's question.
    User question: {question}
    Neo4j query results:
    {query_results}
    Based on the query results, provide a clear and concise answer to the user's question.
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
        input=st.session_state["chat_input"])

    # Vector search with user input
    vsc = VectorSearchClient()
    index = vsc.get_index(endpoint_name="vs_endpoint", index_name="workspace.default.speakers_index")

    results = index.similarity_search(
        columns=["Embeddings", "Concat"],
        query_vector=embeded_input.embeddings[0],  # Replace with your actual query vector
    )

    concat_strings = []
    for result in results["result"]["data_array"]:
        concat_strings.append(result[1])

    # Generate response prompt
    prompt = generate_query_context_prompt(st.session_state["chat_input"], ";".join(concat_strings))
    responseA = ChatCompletion.create(model="databricks-meta-llama-3-70b-instruct",
                                    messages=[{"role": "system", "content": "You are a helpful assistant."},
                                            {"role": "user","content": prompt}],
                                    max_tokens=128)

    # Generate context for neo4j
    prompt = generate_cypher_prompt(st.session_state["chat_input"], neo4j_schema, responseA.response["choices"][0]["message"]["content"])
    responseB = ChatCompletion.create(model="databricks-meta-llama-3-70b-instruct",
                                    messages=[{"role": "system", "content": "You are a helpful assistant."},
                                            {"role": "user","content": prompt}],
                                    max_tokens=128)

    # Generate cipher query
    cipher_query = responseB.response["choices"][0]["message"]["content"]
    print(cipher_query)

    # Fetch data from neo4j
    graph_records = []
    with GraphDatabase.driver(f"{NEO4J_PROTOCOL}{NEO4J_CONNECTION_URL}", auth=(NEO4J_USER, NEO4J_PASSWORD)) as driver:
        records,_,_ = driver.execute_query(cipher_query, database_="neo4j")
        for record in records:
            graph_records.append(list(record.data().items()))
    print(graph_records)

    # Generate the final response
    prompt = generate_response_prompt(st.session_state["chat_input"], graph_records)
    responseC = ChatCompletion.create(model="databricks-meta-llama-3-70b-instruct",
                                    messages=[{"role": "system", "content": "You are a helpful assistant."},
                                            {"role": "user","content": prompt}],
                                    max_tokens=128)

    # Write response to chat history
    st.session_state["chat_history"].append(
        {
            "role": "assistant",
            "content": responseC.response["choices"][0]["message"]["content"]
        },  # This can be replaced with your chat response logic
    )

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

st.chat_input("Enter your message", on_submit=chat_actions, key="chat_input")

for i in st.session_state["chat_history"]:
    with st.chat_message(name=i["role"]):
        st.write(i["content"])
