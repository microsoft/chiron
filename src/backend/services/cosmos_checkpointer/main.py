import os
import asyncio
from dotenv import load_dotenv 
from langchain_openai import AzureChatOpenAI

from typing import Literal
from langchain_core.tools import tool

from langgraph.prebuilt import create_react_agent
#from cosmos_db_saver import CosmosDBSaver
from async_cosmos_db_saver import AsyncCosmosDBSaver


@tool
def get_weather(city: Literal["nyc", "sf"]):
    """Use this to get weather information."""
    if city == "nyc":
        return "It might be cloudy in nyc"
    elif city == "sf":
        return "It's always sunny in sf"
    else:
        raise AssertionError("Unknown city")


tools = [get_weather]


azure_endpoint: str = os.getenv("AZURE_OPENAI_API_ENDPOINT")
azure_openai_api_key: str = os.getenv("AZURE_OPENAI_API_KEY")
azure_openai_api_version: str = os.getenv("AZURE_OPENAI_API_VERSION")
azure_emdedding_deployment: str = os.getenv("AZURE_OPENAI_API_EMBEDDINGS_DEPLOYMENT_NAME")
azure_deployment: str = os.getenv("AZURE_OPENAI_API_DEPLOYMENT_NAME")
cosmos_url: str = os.getenv("AZURE_COSMOSDB_ENDPOINT")       
cosmos_key: str = os.getenv("AZURE_COSMOSDB_KEY") 
cosmos_db: str = os.getenv("AZURE_COSMOSDB_DATABASE_NAME")
cosmos_container: str = os.getenv("AZURE_COSMOSDB_CONTAINER_NAME")
cosmos_write_container: str = os.getenv("AZURE_COSMOSDB_CONTAINER_CHECKPOINT_WRITER")

model = AzureChatOpenAI = AzureChatOpenAI(
    temperature=0,
    azure_deployment=azure_deployment,
    openai_api_version=azure_openai_api_version,
    azure_endpoint=azure_endpoint,
    api_key=azure_openai_api_key,
)

#Sync method call
# with CosmosDBSaver.from_conn_info(url=cosmos_url, key=cosmos_key, db_name=cosmos_db, container_name=cosmos_container, write_container_name=cosmos_write_container ) as checkpointer:
#     graph = create_react_agent(model, tools=tools, checkpointer=checkpointer)
#     config = {"configurable": {"thread_id": "2",
#                                 "checkpoint_ns": "weather"}}
#     res = graph.invoke({"messages": [("human", "what's the weather in sf")]}, config)
#     latest_checkpoint = checkpointer.get(config)
#     latest_checkpoint_tuple = checkpointer.get_tuple(config)
#     checkpoint_tuples = list(checkpointer.list(config))
#     print(graph.invoke({"messages": [("human", "what's the weather in nyc")]}, config))


async def main():
    
    async with AsyncCosmosDBSaver.from_conn_info(
        url=cosmos_url, 
        key=cosmos_key, 
        db_name=cosmos_db, 
        container_name=cosmos_container, 
        write_container_name=cosmos_write_container
    ) as checkpointer:
        graph = create_react_agent(model, tools=tools, checkpointer=checkpointer)
        config = {"configurable": {"thread_id": "2", "checkpoint_ns": "weather"}}
        
        res = await graph.ainvoke({"messages": [("human", "what's the weather in sf")]}, config)
        latest_checkpoint = await checkpointer.aget(config)
        latest_checkpoint_tuple = await checkpointer.aget_tuple(config)
        checkpoint_tuples = [item async for item in checkpointer.alist(config)]
        
        print(await graph.ainvoke({"messages": [("human", "what's the weather in nyc")]}, config))

    
# Run the main function
asyncio.run(main())

