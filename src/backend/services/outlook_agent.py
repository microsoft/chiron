from datetime import datetime
from helper.azure_config import AzureConfig
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.prompts.chat import (
    ChatPromptTemplate,
    MessagesPlaceholder
)
from langchain_core.tools import tool
from langchain_openai import AzureChatOpenAI

config = AzureConfig()

llm = AzureChatOpenAI(
    deployment_name=config.azure_deployment,
    openai_api_version=config.azure_openai_api_version
)  

### Tools ### considering moving to separate directory
@tool
def send_email(message: str, recipients: list[str]) -> str: # I wonder how well other return types might work
    """Send an email to a list of recipients."""
    # todo: add email sending logic
    return f"Sent email: {message} to {', '.join(recipients)}"

@tool
def create_calendar_event(event_name: str, datetime: datetime) -> str:
    """Create a calendar event in Outlook."""
    # todo: add event creation logic
    return f"Created an Outlook on {datetime} event named {event_name}"

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

# helping to check patients
agent = create_openai_tools_agent(llm, tools, prompt)

outlook_agent = AgentExecutor(agent=agent, tools=tools)

__all__ = [outlook_agent]
