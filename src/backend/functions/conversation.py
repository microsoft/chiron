import azure.functions as func
import json
import uuid
from datetime import datetime
from typing import Dict, List
from agents.outlook_agent import outlook_agent
from agents.todo_agent import todo_agent
from helper.azure_config import AzureConfig
from langchain.agents import AgentExecutor
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage
from services.llm_with_tools import acall_llm_with_tools
from services.supervisor import Supervisor

conversationBp = func.Blueprint()


@conversationBp.route(route="conversation", methods=["POST"])
async def converse(req: func.HttpRequest) -> func.HttpResponse:
    try:
        body = req.get_json()

        config = AzureConfig()

        # UI sends the full conversation, we only want what the user said
        last_msg = body.get("messages")[-1]

        human_msg = HumanMessage(**last_msg)

        # credential = DefaultAzureCredential()

        llm = AzureChatOpenAI(
            deployment_name=config.azure_openai_chat_deployment,
            openai_api_version=config.azure_openai_chat_api_version,
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

        langchain_messages: List[BaseMessage] = []
        openai_messages = []

        if config.use_supervisor:
            agents: Dict[str, AgentExecutor] = {
                "OutlookAgent": outlook_agent,
                "TodoAgent": todo_agent,
            }

            supervisor = Supervisor(
                config,
                """You are a Supervisor LLM responsible for orchestrating interactions
                between the user and two specialized agents: the Outlook Management Agent and
                the To-Do List Management Agent. Your primary function is to delegate
                tasks to the appropriate agent based on the user’s requests and ensure
                seamless coordination between the agents.""",
                agents,
            )

            langchain_messages: List[BaseMessage] = await supervisor.arun(
                {"messages": [human_msg]}
            )
        else:
            resp: List[BaseMessage] = await acall_llm_with_tools(llm, human_msg)

            langchain_messages = [resp]

        for msg in langchain_messages:
            if msg.type != "human":
                dict_msg = msg.dict()
                openai_messages.append(
                    {
                        "name": (
                            dict_msg["name"]
                            if "name" in dict_msg
                            else "Your LLM Assistant"
                        ),
                        "id": msg.id,
                        "role": "assistant",
                        "content": msg.content,
                        "date": (
                            dict_msg["date"]
                            if "date" in dict_msg
                            else datetime.now().isoformat()
                        ),
                    }
                )

        response_body = {
            "id": str(uuid.uuid4()),
            # created: number... I think this is a timestamp
            "created": datetime.now().isoformat(),
            "choices": [{"messages": openai_messages}],
            # front end uses this to determine if streaming or not, we're not currently and breaking
            # streaming with some of the front end modifications to show separate agents... out of scope of sprint
            "object": "chat.completion",
        }

        return func.HttpResponse(json.dumps(response_body), status_code=200)
    except Exception as e:
        return func.HttpResponse(str(e), status_code=500)
