from tidb_vector.integrations import TiDBVectorClient
from src.utils.openai.embeddings.generate_embeddings import get_embeddings
import pandas as pd
import json


def run_embedding_script(file_path: str, embedding_column: str, table_name: str):
    vector_store = TiDBVectorClient(
        table_name=f"{table_name}",
        connection_string="",
        vector_dimension=1536,
        drop_existing_table=True,
    )

    # Load the CSV file from file_path
    df = pd.read_csv(file_path)

    # Extract the 'text' column and generate embeddings
    texts = df[embedding_column].tolist()
    embeddings = [get_embeddings(text) for text in texts]

    # Save the list to a JSON file
    try:
        with open(f"data/{table_name}.json", "w") as file:
            json.dump(embeddings, file)
    except Exception as e:
        pass
    """
    df = pd.read_csv(file_path)
    texts = df[embedding_column].tolist()

    with open(f"data/logos_cleaned_embeddings.json", "r") as file:
        embeddings = json.load(file)
    """
    metadata = df.drop(columns=[embedding_column]).to_dict(orient="records")

    # Insert vectors into the vector store
    vector_store.insert(texts=texts, embeddings=embeddings, metadatas=metadata)
