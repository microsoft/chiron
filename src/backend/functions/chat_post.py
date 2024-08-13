import json
import azure.functions as func
from helper.azure_config import AzureConfig
from services.chat_service import ChatService

chatBp = func.Blueprint() 
store={}
cosmos_db=None

@chatBp.route(route="chat-post", methods=["POST"])
def runChat(req: func.HttpRequest) -> func.HttpResponse:    
    # global cosmos_db
    # logging.info('Python HTTP trigger function processed a request.')
    request_body = req.get_json()
    user_question = request_body.get('messages')
    user_id = request_body.get('user_id')
    session_id = request_body.get('session_id')
    if not user_question or len(user_question) == 0:
        return func.HttpResponse(json.dumps({'error': 'Invalid or missing messages in the request body'}),
                                 status_code=400)
    
    config = AzureConfig()

    try:
        chat_service = ChatService(config, user_id, session_id)
        response = chat_service.chat(user_question)
        return func.HttpResponse(response, status_code=200)
    except Exception as e:
        return func.HttpResponse(json.dumps({'error': str(e)}), status_code=500)
