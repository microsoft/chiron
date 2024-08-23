from helper.azure_config import AzureConfig
from langchain_core.tools import tool
from langchain.tools import Tool
from langchain.tools.retriever import create_retriever_tool
from langchain_openai import AzureOpenAIEmbeddings
# from langchain_community.document_loaders import TextLoader
from langchain_community.retrievers import AzureAISearchRetriever
# from langchain_community.vectorstores.azuresearch import AzureSearch
# from langchain_text_splitters import CharacterTextSplitter

class AISearch:
    def __init__(self, azure_search_endpoint, azure_search_key):
        self.azure_search_endpoint = azure_search_endpoint
        self.azure_search_key = azure_search_key


config = AzureConfig()
aiSearch = AISearch(config.vector_store_address,config.vector_store_password)

@tool
def select_index() -> Tool:
    """Select the index to be used for the retriever tool based on the user intent."""
    index_list = [
        # {"name": "ithelpnow", "description": "IT HelpNow index. While answering think step-by-step and justify your answer.Please add source document file names also in the input_variables section and as reference documents."},
        # {"name": "salestraining", "description": "Searches and returns information about the product training material. This index is useful for any technical or sales related questions.Please add source document file names also in the input_variables section and as reference documents.Please give  _get_relevant_documents data in json"},
        # {"name": "marketing", "description": "For the Market Intelligence team. The ingested documents are public information about Intuitive’s competitors (sourced by the Marketing team), internal analysis of competitors and guidelines on how to engage in competitive conversations.Please add source document file names also in the input_variables section and as reference documents.Please give  _get_relevant_documents data in json"},
        # {"name": "complaints", "description": "For the PMS Reportability (RAQA) team. The ingested documents are Work Instructions and guidance documents. The chatbot provides the complaints team a resource to help classify complaint symptoms, and augment their tasks. The chatbot is not linked to EDW so you cannot query complaint data or understand specific complaint data at this time. Please give  _get_relevant_documents data in json."}
        {"name": "apiindex-2", "description": "Everything there is to know about watches, their operation and maintenance. Please respond in json format"},
        {"name": "langchain-vector-openapi", "description": "Everything we know about available API endpoints, their functionality and their OpenAPI definitions. Please respond in json format."}
    ]

    ### loop through the index_list and create a retriever tool for each index
    retriever_tools:Tool = [
        create_retriever_tool(
            AzureAISearchRetriever(
                service_name=aiSearch.azure_search_endpoint,
                api_key=aiSearch.azure_search_key,
                content_key="text", 
                top_k=10, 
                index_name=index["name"],
            ),
            name=index["name"],
            description=index["description"],
        )
        for index in index_list
    ]
    
    return retriever_tools

# @tool
# def load_document():
#     """Retrieve documents from a text file and store them in a vector store."""
#     loader = TextLoader("state_of_the_union.txt")

#     documents = loader.load()
#     text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
#     texts = text_splitter.split_documents(documents)
#     aoai_embeddings = AzureOpenAIEmbeddings()
#     document_vector = AzureSearch.from_documents(texts, aoai_embeddings)
#     # document_vector = AzureSearch.semantic_hybrid_search()
#     return document_vector


# @tool
# def retrieve_documents(query: str):
#     """Retrieve relevant documents from a vector store based on a query."""    
#     docs=vector_store.similarity_search(
#         query=query,
#         k=3,
#         search_type="similarity",
#     )
#     # print(docs[0].page_content)

#     aoai_embeddings = AzureOpenAIEmbeddings()
#     vectorstore = AzureSearch.from_documents(docs, aoai_embeddings)
#     return vectorstore.retrieve_documents("state of the union")

__all__ = [select_index]