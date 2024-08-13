import azure.functions as func 
from functions.chat_post import chatBp
from functions.health_check import healthCheckBp
#from functions.index_trigger import indexTriggerBp

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION) 

app.register_functions(healthCheckBp)
app.register_functions(chatBp) 

# commented out until we settle on architecture
#app.register_functions(indexTriggerBp)

