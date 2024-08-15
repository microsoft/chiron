import json
import azure.functions as func

frontendSettingsBp = func.Blueprint() 

@frontendSettingsBp.route(route="frontend_settings", methods=["GET"])
def runFrontendSettings(req: func.HttpRequest) -> func.HttpResponse:    
    frontend_settings = json.dumps({
        "auth_enabled": False,
        "feedback_enabled": (
            False
        ),
        "ui": {
            "title": "Chiron",
            "logo": "", # no longer needed...
            "chat_logo": "", # no longer needed...
            "chat_title": "Chiron Chat",
            "chat_description": "Our starter chat",
            "show_share_button": False,
            "show_chat_history_button": False,
        },
        "sanitize_answer": True,
    })
    
    return func.HttpResponse(frontend_settings, status_code=200)