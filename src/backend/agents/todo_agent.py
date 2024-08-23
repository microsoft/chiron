from services.log_handler import LogHandler
from helper.azure_config import AzureConfig
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.prompts.chat import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import AzureChatOpenAI
from tools.todo_tools import create_todo, list_todos, complete_todo, delete_todo, update_todo

config = AzureConfig()

llm = AzureChatOpenAI(
    deployment_name=config.azure_openai_chat_deployment,
    openai_api_version=config.azure_openai_chat_api_version,
)

system_prompt = """You are a To-Do List Management Agent. Your primary function
is to help users manage their tasks efficiently. You can add, remove, update, 
and list tasks. You can also set deadlines and priorities for tasks."""

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

tools = [create_todo, list_todos, complete_todo, delete_todo, update_todo]

agent = create_openai_tools_agent(llm, tools, prompt)

todo_agent = AgentExecutor(agent=agent, tools=tools, callbacks=[LogHandler("todo_agent_executor")])

__all__ = [todo_agent]
