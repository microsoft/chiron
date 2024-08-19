from datetime import datetime
from typing import Dict, List
import functools
import operator
from helper.azure_config import AzureConfig
from langchain.agents import AgentExecutor
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.prompts.chat import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import AzureChatOpenAI
from langgraph.graph import StateGraph, END
from typing import Annotated, Sequence, TypedDict
import uuid

# from langchain_community.adapters import convert
# from openai import ChatCompletion

# https://langchain-ai.github.io/langgraph/tutorials/multi_agent/agent_supervisor/#construct-graph
# https://langchain-ai.github.io/langgraph/how-tos/pass-run-time-values-to-tools


class Supervisor:
    def __init__(
        self, config: AzureConfig, system_prompt: str, agents: Dict[str, AgentExecutor]
    ):

        # credential = DefaultAzureCredential()

        llm = AzureChatOpenAI(
            deployment_name=config.azure_deployment,
            openai_api_version=config.azure_openai_api_version,
            # azure_endpoint=config.azure_endpoint,
            # todo: mi / env var
            # azure_ad_token_provider=credential.get_token
            # error:
            #   'DefaultAzureCredential failed to retrieve a token from the included
            #    credentials.\nAttempted credentials:\n\tEnvironmentCredential:
            #    EnvironmentCredential authentication unavailable. Environment variables
            #    are not fully configured.\nVisit
            #    https://aka.ms/azsdk/python/identity/environmentcredential/troubleshoot
            #    to troubleshoot this issue.\n\tManagedIdentityCredential: "get_token" requires
            #    at least one scope\nTo mitigate this issue, please refer to the troubleshooting
            #    guidelines here at
            #    https://aka.ms/azsdk/python/identity/defaultazurecredential/troubleshoot.,
            #    NoneType: None'
        )

        members = [agent_name for agent_name, agent in agents.items()]

        system_prompt = (
            "You are a supervisor tasked with managing a conversation between the"
            " following workers:  {members}. Given the following user request,"
            " respond with the worker to act next. Each worker will perform a"
            " task and respond with their results and status. When finished,"
            " respond with FINISH."
        )

        # Our team supervisor is an LLM node. It just picks the next agent to process
        # and decides when the work is completed
        options = ["FINISH"] + members

        # Using openai function calling can make output parsing easier for us
        function_def = {
            "name": "route",
            "description": "Select the next role.",
            "parameters": {
                "title": "routeSchema",
                "type": "object",
                "properties": {
                    "next": {
                        "title": "Next",
                        "anyOf": [
                            {"enum": options},
                        ],
                    }
                },
                "required": ["next"],
            },
        }

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder(variable_name="messages"),
                (
                    "system",
                    "Given the conversation above, who should act next?"
                    " Or should we FINISH? Select one of: {options}",
                ),
            ]
        ).partial(options=str(options), members=", ".join(members))
        supervisor_chain = (
            prompt
            | llm.bind_functions(functions=[function_def], function_call="route")
            | JsonOutputFunctionsParser()
        )

        workflow = StateGraph(AgentState)

        for agent_name, agent in agents.items():
            node = functools.partial(self.__agent_node__, agent=agent, name=agent_name)
            workflow.add_node(agent_name, node)

        for member in members:
            # We want our workers to ALWAYS "report back" to the supervisor when done
            workflow.add_edge(member, "supervisor")

        # The supervisor populates the "next" field in the graph state
        # which routes to a node or finishes
        # our conditional map is the agents and the finish state
        conditional_map = {k: k for k in members}
        conditional_map["FINISH"] = END
        # is there the possibility and value in having additiona conditional edges? what would be their src
        workflow.add_conditional_edges(
            "supervisor", self.__should_continue__, conditional_map
        )
        workflow.add_node("supervisor", supervisor_chain)
        # does the conditional edge need to be the entry point?
        workflow.set_entry_point("supervisor")
        self.graph = workflow.compile()

    def __agent_node__(self, state, agent, name):
        result = agent.invoke(state)
        return {"messages": [AIMessage(content=result["output"], name=name, id=str(uuid.uuid4()), date=str(datetime.now().isoformat()))]}

    def __should_continue__(self, state, config):
        print(state)
        print(config)

        # the value of the next field is the key in the conditional map
        # if our conditional map is just a dictionary of string, string
        # why can't this function just return the value of the dictionary element?
        # is there some value to that layer of abstraction?
        return state["next"]

    async def arun(self, in_messages: List[BaseMessage]) -> List[BaseMessage]:  # is that typing right?
        state = self.graph.invoke(in_messages)
        out_messages: List[BaseMessage] = state["messages"]
        return out_messages


# The agent state is the input to each node in the graph
class AgentState(TypedDict):
    # The annotation tells the graph that new messages will always
    # be added to the current states
    messages: Annotated[Sequence[BaseMessage], operator.add]
    # The 'next' field indicates where to route to next
    next: str
