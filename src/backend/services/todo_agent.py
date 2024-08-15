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
import uuid

class Todo:
    def __init__(self, task: str, due_date: datetime, tags: list[str] = []):
        self.id = str(uuid.uuid4())
        self.task = task
        self.due_date = due_date
        self.completed = False
        self.tags = tags

config = AzureConfig()

llm = AzureChatOpenAI(
    deployment_name=config.azure_deployment,
    openai_api_version=config.azure_openai_api_version
)  
todos = []

### Tools ### considering moving to separate directory
@tool
def create_todo(todo: str, datetime: datetime) -> Todo: # add optional tags and due date for end of week
    """Create a new todo."""
    todos.append(Todo(todo, datetime))
    return Todo

@tool
def list_todos() -> list[Todo]: # todo order by priority, and use optional filter on tags
    """List todos out."""
    return todos

@tool
def complete_todo(todo_id: str) -> Todo:
    """Marks todo as complete."""
    for todo in todos:
        if todo.id == todo_id:
            todo.completed = True
            return todo
    return None

@tool
def delete_todo(todo_id: str) -> bool:
    """Deletes a todo."""
    for todo in todos:
        if todo.id == todo_id:
            todos.remove(todo)
            return True
    return False

@tool
def update_todo(todo_id: str, todo: str, datetime: datetime) -> Todo:
    """Updates a todo."""
    for todo in todos:
        if todo.id == todo_id:
            todo.task = todo
            todo.due_date = datetime
            return todo
    return None

system_prompt = '''You are a To-Do List Management Agent. Your primary function
is to help users manage their tasks efficiently. You can add, remove, update, 
and list tasks. You can also set deadlines and priorities for tasks.'''

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

todo_agent = AgentExecutor(agent=agent, tools=tools)

__all__ = [todo_agent]
