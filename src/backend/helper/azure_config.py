import os
from dotenv import find_dotenv, load_dotenv 

class AzureConfig:
    def __init__(self):
        env_path = find_dotenv()
        load_dotenv(env_path, override=True)
        self.azure_endpoint: str = os.getenv("AZURE_OPENAI_API_ENDPOINT")
        self.azure_openai_api_key: str = os.getenv("AZURE_OPENAI_API_KEY")
        self.azure_openai_chat_deployment: str = os.getenv("AZURE_OPENAI_API_DEPLOYMENT_NAME")
        self.azure_openai_chat_api_version: str = os.getenv("AZURE_OPENAI_API_VERSION")
        self.use_supervisor: bool = True
        self.azure_deployment = os.getenv("AZURE_OPENAI_API_EMBEDDINGS_DEPLOYMENT_NAME")
        self.vector_store_address = os.getenv("AZURE_AISEARCH_ENDPOINT")
        self.vector_store_password = os.getenv("AZURE_AISEARCH_KEY")
        self.azure_openai_api_version = os.getenv("AZURE_OPENAI_API_VERSION")
        self.azure_emdedding_deployment = os.getenv("AZURE_OPENAI_API_EMBEDDING_DEPLOYMENT_NAME")