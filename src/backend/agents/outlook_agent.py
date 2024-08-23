from helper.azure_config import AzureConfig
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.prompts.chat import (
    ChatPromptTemplate,
    MessagesPlaceholder
)
from langchain_openai import AzureChatOpenAI
from tools.outlook_tools import send_email, create_calendar_event

config = AzureConfig()

llm = AzureChatOpenAI(
    deployment_name=config.azure_openai_chat_deployment,
    openai_api_version=config.azure_openai_chat_api_version,
    azure_endpoint=config.azure_endpoint
)

system_prompt = '''You are a Microsoft Outlook Management Agent. Your primary function
is to assist users with managing their emails, calendar events, contacts, and tasks 
within Microsoft Outlook. You can send, read, delete, and organize emails, schedule
and manage calendar events, and handle contacts and tasks.'''

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

tools = [send_email, create_calendar_event]

agent = create_openai_tools_agent(llm, tools, prompt)

outlook_agent = AgentExecutor(agent=agent, tools=tools)

__all__ = [outlook_agent]
