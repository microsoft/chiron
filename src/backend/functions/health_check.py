import azure.functions as func

healthCheckBp = func.Blueprint() 

@healthCheckBp.route(route="health", methods=["GET"])
def runHealthCheck(req: func.HttpRequest) -> func.HttpResponse:    
        return func.HttpResponse("Healthy", status_code=200)