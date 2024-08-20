import azure.functions as func 
from functions.health_check import healthCheckBp
from functions.frontend_settings import frontendSettingsBp
from functions.conversation import conversationBp

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION) 

app.register_functions(healthCheckBp)

app.register_blueprint(frontendSettingsBp)
app.register_functions(conversationBp)
