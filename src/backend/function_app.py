import azure.functions as func 
from functions.chat_post import chatBp
from functions.health_check import healthCheckBp
from functions.frontend_settings import frontendSettingsBp
from functions.conversation import conversationBp
from functions.testing_chat import testChatBp

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION) 

app.register_functions(healthCheckBp)
app.register_functions(chatBp) 

app.register_blueprint(frontendSettingsBp)
app.register_functions(conversationBp)

app.register_blueprint(testChatBp)
