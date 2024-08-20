from datetime import datetime
import json
from langchain_core.tools import tool
from typing import List
import uuid

class Todo:
    def __init__(self, task: str, due_date: datetime, tags: list[str] = []):
        self.id = str(uuid.uuid4())
        self.task = task
        self.due_date = due_date
        self.completed = False
        self.tags = tags

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__ if not isinstance(o, datetime) else o.isoformat())

todos: List[Todo] = [
    Todo("Take the cat to the vet", datetime(2024, 8, 31)),
    Todo("Take son to dentist", datetime(2024, 8, 16)),
    Todo("Get groceries", datetime(2024, 8, 17)),
    Todo("Get my head checked", datetime(1980, 12, 25)),
]

@tool
def create_todo(
    todo: str, datetime: datetime
) -> Todo:  # add optional tags and due date for end of week
    """Create a new todo."""
    new_todo = Todo(todo, datetime)
    todos.append(new_todo)
    return new_todo.toJson() 


# explore other tool options e.g. content_and_artifact
@tool  # (parse_docstring=True, response_format="content_and_artifact") # 
def list_todos() -> str:  # todo order by priority, and use optional filter on tags
    """List out todos on todo list.
    
    Args:
        query: The user's search going to Azure AI Search looking for somethings...
        k: the number of results to return
    
    """  # todo: add arg descriptions to tool descriptions
    todo_json = json.dumps([todo.toJson() for todo in todos])  # list[Todo]
    return todo_json, todos


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
            return todo.toJson()
    return None

__all__ = [create_todo, list_todos, complete_todo, delete_todo, update_todo]
