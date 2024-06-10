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

### Installation

1. **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/summitconnect.git
    cd summitconnect
    ```

2. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3. **Set up Neo4j**:
    - Sign up for Neo4j Aura and get your credentials.
    - Update your Neo4j credentials in the script or environment variables.

4. **Run the application**:
    ```bash
    python app.py
    ```

### Usage

1. **Data Processing**:
    - Use the `process_data.py` script to clean and process the provided data.
    - The script will normalize and clean the data, then upload it to the Neo4j database.

2. **Querying**:
    - Use the `generate_cypher_prompt` function to translate natural language questions into Cypher queries.
    - Use the `generate_response_prompt` function to synthesize responses to user queries using context retrieved from the vector database.

### Challenges

- **Data Consistency**: Normalizing and cleaning data with various formats, missing values, and inconsistent formatting.
- **Identifying Valuable Metadata**: Determining the most valuable metadata for modeling in Neo4j and embedding in Mosaic AI Vector Search.
- **Modeling Data for Neo4j**: Designing a schema to accurately represent complex relationships between speakers, sessions, topics, and companies.
- **Curation of Vectorized Metadata**: Ensuring relevant metadata properties for embedding comparisons to user queries.

### Contributing

We welcome contributions to SummitConnect! Please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes.
4. Commit your changes (`git commit -m 'Add new feature'`).
5. Push to the branch (`git push origin feature-branch`).
6. Open a pull request.

### License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

### Contact

For any questions or inquiries, please contact us at [your.email@example.com](mailto:your.email@example.com).

---

Elevate your experience at the Data + AI Summit 2024 with SummitConnect and make every connection count.
