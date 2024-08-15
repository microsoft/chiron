from helper.azure_config import AzureConfig

from typing import Annotated, Literal, TypedDict
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph, MessagesState
from langgraph.prebuilt import ToolNode

# Example from: https://langchain-ai.github.io/langgraph/tutorials/introduction/#part-1-build-a-basic-chatbot

class AgentService:
    def __init__(self, config: AzureConfig, user_id: str, session_id: str):        
        # Define the tools for the agent to use
        @tool
        def search(query: str):
            """Call to surf the web."""
            # This is a placeholder, but don't tell the LLM that...
            if "sf" in query.lower() or "san francisco" in query.lower():
                return "It's 60 degrees and foggy."
            return "It's 90 degrees and sunny."

        self.user_id = user_id
        self.session_id = session_id

        self.tools = [search]
        self.tool_node = ToolNode(self.tools)

        self.model = AzureChatOpenAI(
                    temperature=0.3,
                    azure_deployment=config.azure_deployment,
                    openai_api_version=config.azure_openai_api_version,
                    azure_endpoint=config.azure_endpoint,
                    api_key=config.azure_openai_api_key,
                ).bind_tools(self.tools)

        # Define the function that determines whether to continue or not
        def should_continue(state: MessagesState) -> Literal["tools", END]:
            messages = state['messages']
            last_message = messages[-1]
            # If the LLM makes a tool call, then we route to the "tools" node
            if last_message.tool_calls:
                return "tools"
            # Otherwise, we stop (reply to the user)
            return END


        # Define the function that calls the model
        def call_model(state: MessagesState):
            messages = state['messages']
            response = self.model.invoke(messages)
            # We return a list, because this will get added to the existing list
            return {"messages": [response]}


        # Define a new graph
        workflow = StateGraph(MessagesState)

        # Define the two nodes we will cycle between
        workflow.add_node("agent", call_model)
        workflow.add_node("tools", self.tool_node)

        workflow.set_entry_point("agent")

        # We now add a conditional edge
        workflow.add_conditional_edges(
            "agent",
            should_continue,
        )

        # We now add a normal edge from `tools` to `agent`.
        # This means that after `tools` is called, `agent` node is called next.
        workflow.add_edge("tools", 'agent')

        # Initialize memory to persist state between graph runs
        checkpointer = MemorySaver()

        self.app = workflow.compile(checkpointer=checkpointer)                             

    def chat(self, user_msg: str) -> str:
        # Use the Runnable
        final_state = self.app.invoke(
            # {"messages": [HumanMessage(content="what is the weather in sf")]},
            {"messages": [HumanMessage(content=user_msg)]},
            config={"configurable": {"thread_id": self.session_id}}  #thread_id is the session_id
        )
        response=final_state["messages"][-1].content

        return response