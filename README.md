# SummitConnect - data-ai-summit-2024-hackathon

## Connecting Minds, Maximizing Opportunities

### Overview

SummitConnect is an innovative application designed to enhance the networking and learning experiences of attendees at the Data + AI Summit 2024 by Databricks. With 15,000 participants and 836 speakers, navigating the event can be overwhelming. SummitConnect leverages advanced AI and data technologies to help attendees discover and connect with the most relevant speakers, sessions, and topics.

### Features

- **Speaker Discovery**: Find speakers based on their sessions, topics, and backgrounds.
- **Session Insights**: Get detailed information about sessions and the speakers involved.
- **Networking Opportunities**: Identify speakers with similar interests and backgrounds.
- **Semantic Matching**: Use AI-powered search to find speakers with similar biographies and expertise.

### Built With

- **Llama 3**: We used this open-source large language model by Meta for generating the necessary code, ensuring robustness and scalability.
- **Neo4j and Cypher Query Language**: We employed Neo4j for graph database management, allowing us to model and query complex relationships between speakers, topics, and sessions efficiently.
- **Neo4j Aura**: Neo4j Aura is a fully managed cloud service offering by Neo4j, designed to provide a scalable and high-performance graph database solution. For this project, we utilized their free tier.
- **Mosaic AI Vector Search**: This AI-native embedding database facilitated semantic matching, enabling users to find speakers with similar backgrounds, topics, and biographies. We used the Databricks Ecosystem for self-hosting our vector database.
- **BGE Embeddings Model**: Hosted via Databricks, this model provides high-quality embeddings that capture the meaning and context of textual data, enhancing our semantic search capabilities.

# Example of Cypher Query generation using Llama 3 70b

<img width="839" alt="image" src="https://github.com/friedliver/data-ai-summit-2024-hackathon/assets/77113505/de6ccc07-e747-41b3-8fc2-5e8218679ce1">
