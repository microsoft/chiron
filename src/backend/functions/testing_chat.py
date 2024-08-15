from services.outlook_agent import outlook_agent
from services.todo_agent import todo_agent
import azure.functions as func
from helper.azure_config import AzureConfig
from services.chat_service import Supervisor
from typing import Dict
from langchain.agents import AgentExecutor
from langchain_core.load import dumps

# from azure.identity import DefaultAzureCredential

testChatBp = func.Blueprint()

@testChatBp.route(route="test-chat", methods=["POST"])
def runTestChatBp(req: func.HttpRequest) -> func.HttpResponse:
    try:
        body = req.get_json()

        config = AzureConfig()

        config = AzureConfig()

        agents: Dict[str, AgentExecutor] = {
            "OutlookAgent": outlook_agent,
            "TodoAgent": todo_agent
        }

        supervisor = Supervisor(
            config,
            '''You are a Supervisor LLM responsible for orchestrating interactions
            between the user and two specialized agents: the Outlook Management Agent and
            the To-Do List Management Agent. Your primary function is to delegate
            tasks to the appropriate agent based on the user’s requests and ensure
            seamless coordination between the agents.''',
            agents
        )

        response = supervisor.run(body) # messages

        # https://python.langchain.com/v0.2/docs/how_to/serialization
        json_resp = dumps(response)

        return func.HttpResponse(json_resp, status_code=200)
    except Exception as e:
        print(e)
        return func.HttpResponse(str(e), status_code=500)
