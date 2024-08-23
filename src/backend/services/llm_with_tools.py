from langchain_openai import AzureChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from services.log_handler import LogHandler
from tools.outlook_tools import create_calendar_event, send_email
from tools.todo_tools import complete_todo, create_todo, delete_todo, list_todos, update_todo
from typing import List

async def acall_llm_with_tools(llm: AzureChatOpenAI, human_msg: HumanMessage):
    tools = [
        create_todo,
        list_todos,
        complete_todo,
        delete_todo,
        update_todo,
        send_email,
        create_calendar_event,
    ]
    tools_dictionary = {
        "create_todo": create_todo,
        "list_todos": list_todos,
        "complete_todo": complete_todo,
        "delete_todo": delete_todo,
        "update_todo": update_todo,
        "send_email": send_email,
        "create_calendar_event": create_calendar_event,
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

    llm_with_tools.with_config(callbacks=[LogHandler("llm_with_tools")])


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

    chain = {"human_msg": RunnablePassthrough()} | few_shot_prompt | LogHandler("llm_with_tools_chain")

    # https://python.langchain.com/v0.2/docs/how_to/callbacks_attach/
    ai_msg = chain.with_config(callbacks=[LogHandler("llm_with_tools 2")]).invoke(human_msg)

    msgs: List[BaseMessage] = [human_msg, ai_msg]

    for tool_call in ai_msg.tool_calls:
        selected_tool = tools_dictionary[tool_call["name"]]
        tool_msg = selected_tool.with_config(callbacks=[LogHandler("selected_tool")]).invoke(tool_call)
        msgs.append(tool_msg)

    result = llm_with_tools.with_config(callbacks=[LogHandler("llm_with_tools 3")]).invoke(msgs)

    result.name = "YourLLMAssistant"

    return result
