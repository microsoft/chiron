from langchain_openai import AzureChatOpenAI
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from tools.outlook_tools import create_calendar_event, send_email
from tools.todo_tools import complete_todo, create_todo, delete_todo, list_todos, update_todo
from tools.retriever_tools import select_index  #, load_document
from typing import Any, Dict, List, Union

async def acall_llm_with_tools(llm: AzureChatOpenAI, human_msg: HumanMessage):
    tools = [
        create_todo,
        list_todos,
        complete_todo,
        delete_todo,
        update_todo,
        send_email,
        create_calendar_event,
        select_index,
        # load_document,
    ]
    tools_dictionary = {
        "create_todo": create_todo,
        "list_todos": list_todos,
        "complete_todo": complete_todo,
        "delete_todo": delete_todo,
        "update_todo": update_todo,
        "send_email": send_email,
        "create_calendar_event": create_calendar_event,
        "select_index": select_index,
        # "load_document": load_document,
    }

    # few shot option
    # examples = [
    #     HumanMessage(
    #         "What's the product of 317253 and 128472 plus four", name="example_user"
    #     ),
    #     AIMessage(
    #         "",
    #         name="example_assistant",
    #         tool_calls=[
    #             {"name": "Multiply", "args": {"x": 317253, "y": 128472}, "id": "1"}
    #         ],
    #     ),
    #     ToolMessage("16505054784", tool_call_id="1"),
    #     AIMessage(
    #         "",
    #         name="example_assistant",
    #         tool_calls=[{"name": "Add", "args": {"x": 16505054784, "y": 4}, "id": "2"}],
    #     ),
    #     ToolMessage("16505054788", tool_call_id="2"),
    #     AIMessage(
    #         "The product of 317253 and 128472 plus four is 16505054788",
    #         name="example_assistant",
    #     ),
    # ]


    llm_with_tools = llm.bind_tools(tools, tool_choice="auto")

    llm_with_tools.with_config(callbacks=[NamingHandler()])


    system = """You are a To-Do List Management Agent. Your primary function
                is to help users manage their tasks efficiently. You can add, remove, update, 
                and list tasks. You can also set deadlines and priorities for tasks."""
    few_shot_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            # *examples,
            ("human", "{human_msg}"),
        ]
    )

    handler = NamingHandler()

    chain = {"human_msg": RunnablePassthrough()} | few_shot_prompt | llm_with_tools

    # https://python.langchain.com/v0.2/docs/how_to/callbacks_attach/
    ai_msg = chain.with_config(callbacks=[handler]).invoke(human_msg)

    msgs: List[BaseMessage] = [human_msg, ai_msg]

    for tool_call in ai_msg.tool_calls:
        selected_tool = tools_dictionary[tool_call["name"]]
        tool_msg = selected_tool.with_config(callbacks=[handler]).invoke(tool_call)
        msgs.append(tool_msg)

    result = llm_with_tools.with_config(callbacks=[handler]).invoke(msgs)

    result.name = "YourLLMAssistant"

    return result


# https://python.langchain.com/v0.1/docs/modules/callbacks/
class NamingHandler(BaseCallbackHandler):
    """Base callback handler that can be used to handle callbacks from langchain."""

    def on_tool_start(
        self, serialized: Dict[str, Any], input_str: str, **kwargs: Any
    ) -> Any:
        """Run when tool starts running."""
        print(f"\nTool started: {input_str}\n{serialized}\n{kwargs}\n")

    def on_tool_end(self, output: Any, **kwargs: Any) -> Any:
        """Run when tool ends running."""
        print(f"\nTool end: {output}\n{kwargs}\n")

    def on_tool_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> Any:
        """Run when tool errors."""
        print(f"\nTool error: {error}\n{kwargs}\n")


# prompt = ChatPromptTemplate.from_messages(["Tell me a joke about {animal}"])

# # To enable streaming, we pass in `streaming=True` to the ChatModel constructor
# # Additionally, we pass in our custom handler as a list to the callbacks parameter
# model = ChatAnthropic(
#     model="claude-3-sonnet-20240229", streaming=True, callbacks=[MyCustomHandler()]
# )

# chain = prompt | model

# response = chain.invoke({"animal": "bears"})
