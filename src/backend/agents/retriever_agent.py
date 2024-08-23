import helper.azure_config as AzureConfig

from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_community.vectorstores.azuresearch import AzureSearch
from tools.retriever_tools import select_index  #,load_document


config = AzureConfig.AzureConfig()

llm = AzureChatOpenAI(
    deployment_name=config.azure_openai_chat_deployment,
    openai_api_version=config.azure_openai_chat_api_version,
    azure_endpoint=config.azure_endpoint
)

embeddings: AzureOpenAIEmbeddings = AzureOpenAIEmbeddings(
    azure_deployment=config.azure_openai_embedding_deployment,
    openai_api_version=config.azure_openai_chat_api_version,
    azure_endpoint=config.azure_endpoint,
    api_key=config.azure_openai_api_key,
)

vector_store: AzureSearch = AzureSearch(
    azure_search_endpoint=config.vector_store_address,
    azure_search_key=config.vector_store_password,
    index_name=config.index_name,
    embedding_function=embeddings.embed_query,
)

# system_prompt=PromptTemplate.from_template(
#         """Given the user question below, classify it as either being about `API Endpoints`, or `watches`.
#         Do not respond with more than one word.
#         <question>
#         {question}
#         </question>
#         Classification:"""
#     )


system_prompt = '''You are a knowledge agent. Your primary function is to understand user requests and provide which relevent index needs to be consulted based on the information provided. 
    You will need to consult multiple knowledge bases and provide a coherent and accurate answer. Provide your answer along with your reasoning, and if possible, provide references.

    Here are the tools available to you:
    apiindex-2: Everything there is to know about watches, their operation and maintenance. Please respond in json format.
    langchain-vector-openapi: Everything we know about available API endpoints, their functionality and their OpenAPI definitions. Please respond in json format.
'''
#     it_knowledge_agent: A tool that uses Azure AI Search Retrievers to retrieve information from the IT HelpNow index.
#     sales-training_knowledge_agent: A tool that uses Azure AI Search Retrievers to retrieve information from the Sales Training index.
#     complaints_knowledge_agent: A tool that uses Azure AI Search Retrievers to retrieve information from the Competitive Intelligence index.
#     comp_intel_knowledge_agent: A tool that uses Azure AI Search Retrievers to retrieve information  from the Competitive Intelligence index.
# '''

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            system_prompt,
        ),
        MessagesPlaceholder(variable_name="messages"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

tools = [select_index]  #load_document

agent = create_openai_tools_agent(llm, tools, prompt)

retriever_agent = AgentExecutor(agent=agent, tools=tools)

__all__ = [retriever_agent]