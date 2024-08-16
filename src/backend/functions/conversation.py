from datetime import datetime
import json
import uuid
import azure.functions as func
from helper.azure_config import AzureConfig
from services.outlook_agent import outlook_agent
from services.todo_agent import todo_agent
import azure.functions as func
from helper.azure_config import AzureConfig
from services.superivsor import Supervisor
from typing import Dict, List
from langchain.agents import AgentExecutor

from langchain_core.messages import BaseMessage, HumanMessage

conversationBp = func.Blueprint()


@conversationBp.route(route="conversation", methods=["POST"])
async def converse(req: func.HttpRequest) -> func.HttpResponse:
    try:
        body = req.get_json()

        config = AzureConfig()

        agents: Dict[str, AgentExecutor] = {
            "OutlookAgent": outlook_agent,
            "TodoAgent": todo_agent,
        }

        # UI sends the full conversation, we only want what the user said
        last_msg = body.get("messages")[-1]

        human_msg = HumanMessage(**last_msg)

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

        openai_messages = []

        for msg in langchain_messages:
            if msg.type != "human":
                openai_messages.append(
                    {
                        "name": msg.name,
                        "id": msg.id,
                        "role": "assistant",
                        "content": msg.content,
                        "date": msg.dict()["date"],
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
