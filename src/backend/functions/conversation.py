from datetime import datetime
import json
import uuid
import azure.functions as func
from services.superivsor import Supervisor

conversationBp = func.Blueprint()


@conversationBp.route(route="conversation", methods=["POST"])
def converse(req: func.HttpRequest) -> func.HttpResponse:
    try:
        body = req.get_json()
        unclean_messages = body["messages"]
        messages_with_tools = [obj for obj in unclean_messages if obj]
        messages = [obj for obj in messages_with_tools if obj["role"] != "tool"]
        last_message = messages[-1]
        response_body = {
            # id: string
            "id": str(uuid.uuid4())  # unclear if I should generate these...
            # created: number
            ,"created": datetime.now().isoformat()
            # choices: ChatResponseChoice[]
            ,"choices": [{"messages": messages + # would have been really nice to use expansion syntax
                [{
                    # id: string
                    "id": str(uuid.uuid4())  # unclear if I should generate these...
                    # role: string
                    ,"role": "user" if last_message["role"] == "assistant" else "assistant" # I kind of like this actually
                    # content: string
                    ,"content": "pong" if last_message["content"] == "ping" else "...??"
                    # date: string
                     ,"date": datetime.now().isoformat()

                    # ??
                    # end_turn?: boolean
                    # feedback?: Feedback
                    # context?: string
                }]
            }]
            # object: ChatCompletionType
            ,"object": "chat.completion"  # we're not streaming so just hard code as this
            # model: string
            ,"model": "gpt-3.5-turbo",  # we can pass this in but I am curious if this is needed
            # error?: any
            # history_metadata: {
            #   conversation_id: string
            #   title: string
            #   date: string
            # }
        }

        print(response_body["choices"][-1]["messages"][-1])

        return func.HttpResponse(json.dumps(response_body), status_code=200)
    except Exception as e:
        return func.HttpResponse(str(e), status_code=500)