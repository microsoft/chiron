from datetime import datetime
from helper.azure_config import AzureConfig
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.prompts.chat import (
    ChatPromptTemplate,
    MessagesPlaceholder
)
import os
from langchain_core.tools import tool
from langchain_openai import AzureChatOpenAI
from langchain_community.retrievers import AzureAISearchRetriever
from langchain.tools.retriever import create_retriever_tool
from langchain_core.retrievers import BaseRetriever
from langchain_openai import AzureOpenAIEmbeddings, OpenAIEmbeddings
from langchain.tools.retriever import create_retriever_tool
from langchain_community.vectorstores import AzureSearch
config = AzureConfig()

llm = AzureChatOpenAI(
    deployment_name=config.azure_openai_chat_deployment,
    openai_api_version=config.azure_openai_chat_api_version,
)  

os.environ["AZURE_AI_SEARCH_SERVICE_NAME"] = config.vector_store_address
os.environ["AZURE_AI_SEARCH_API_KEY"] = config.vector_store_password



index_list = [
    {"name": "ithelpnow", "description": "read the following context to answer the question. While answering think step-by-step and justify your answer.Please add source document file names also in the input_variables section and as reference documents."},
    {"name": "salestraining", "description": "Searches and returns information about the product training material. This index is useful for any technical or sales related questions.Please add source document file names also in the input_variables section and as reference documents.Please give  _get_relevant_documents data in json"},
    {"name": "marketing", "description": "For the Market Intelligence team. The ingested documents are public information about Intuitive’s competitors (sourced by the Marketing team), internal analysis of competitors and guidelines on how to engage in competitive conversations.Please add source document file names also in the input_variables section and as reference documents.Please give  _get_relevant_documents data in json"},
    {"name": "complaints", "description": "For the PMS Reportability (RAQA) team. The ingested documents are Work Instructions and guidance documents. The chatbot provides the complaints team a resource to help classify complaint symptoms, and augment their tasks. The chatbot is not linked to EDW so you cannot query complaint data or understand specific complaint data at this time. Please give  _get_relevant_documents data in json."}
]

### loop through the index_list and create a retriever tool for each index
retriever_tools = [
                        create_retriever_tool(
                            AzureAISearchRetriever(
                            content_key="text", top_k=10, index_name=index["name"]
                        ),
                            name=index["name"],
                            description=index["description"],
                           
                    )
                    for index in index_list
                    ]


 
system_prompt = '''You are a knowledge agent. Your primary function is to understand user requests and provide which relevent index needs to be consulted based on the information provided. You will need to consult multiple knowledge bases and provide a coherent and accurate answer. Provide your answer along with your reasoning, and if possible, provide references.


    Here are the tools available to you:
   
    it_knowledge_agent: A tool that uses Azure AI Search Retrievers to retrieve information from the IT HelpNow index.
    sales-training_knowledge_agent: A tool that uses Azure AI Search Retrievers to retrieve information from the Sales Training index.
    complaints_knowledge_agent: A tool that uses Azure AI Search Retrievers to retrieve information from the Competitive Intelligence index.
    comp_intel_knowledge_agent: A tool that uses Azure AI Search Retrievers to retrieve information  from the Competitive Intelligence index.


'''

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


agent = create_openai_tools_agent(llm, retriever_tools, prompt)
knowledge_agent = AgentExecutor(agent=agent, tools=retriever_tools)

__all__ = [knowledge_agent]
