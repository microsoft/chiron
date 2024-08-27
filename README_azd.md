# Deployment
This project supports `azd` for easy deployment of the complete application, as defined in the main.bicep resources. 

## Deploying with the Azure Developer CLI

> **IMPORTANT:** In order to deploy and run this example, you'll need an **Azure subscription with access enabled for the Azure OpenAI service**. You can request access [here](https://aka.ms/oaiapply). You can also visit [here](https://azure.microsoft.com/free/cognitive-search/) to get some free Azure credits to get you started. Your Azure Account must have `Microsoft.Authorization/roleAssignments/write` permissions, such as [User Access Administrator](https://learn.microsoft.com/azure/role-based-access-control/built-in-roles#user-access-administrator) or [Owner](https://learn.microsoft.com/azure/role-based-access-control/built-in-roles#owner).

> **AZURE RESOURCE COSTS** by default this sample will create a Static Web App (SWA) resource that has a monthly cost, as well as Azure OpenAI and storage resources that have per-usage costs. You can switch to a free versions of the SWA if you want to avoid this cost by changing the parameters file under the infra folder (though you will have to change to a managed API)

## Opening the project

This project has [Dev Container support](https://code.visualstudio.com/docs/devcontainers/containers), so it will be be setup automatically if you open it in Github Codespaces or in local VS Code with the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers).

If you're not using one of those options for opening the project, then you'll need to:

1. Install prerequisites:

    - [Azure Developer CLI](https://aka.ms/azure-dev/install)
    - [Python 3+](https://www.python.org/downloads/)
        - **Important**: Python and the pip package manager must be in the path in Windows for the setup scripts to work.
    - [Node.js](https://nodejs.org/en/download/)
    - [Git](https://git-scm.com/downloads)
    - [Powershell 7+ (pwsh)](https://github.com/powershell/powershell) - For Windows users only.
    - **Important**: Ensure you can run `pwsh.exe` from a PowerShell command. If this fails, you likely need to upgrade PowerShell.


### Deploying from scratch:

If you don't have any pre-existing Azure services (i.e. OpenAI or Cognitive Search service), then you can provision
all resources from scratch by following these steps:

1. Run `azd auth login` to login to your Azure account.
1. Run `azd up` to provision Azure resources and deploy this sample to those resources. This also runs a script to build the search index based on files in the `./data` folder.
    * For the target location, the only US region that currently support the models used in this sample and static web apps is **East US 2**. For an up-to-date list of regions and models, check [here](https://learn.microsoft.com/en-us/azure/cognitive-services/openai/concepts/models)
1. After the application has been successfully deployed you will see a URL printed to the console.  Click that URL to interact with the application in your browser.
    > NOTE: It may take a minute for the application to be fully deployed. If you see a "Python Developer" welcome screen, then wait a minute and refresh the page.

### Using existing resources:

If you have existing Azure resources that you want to reuse, then you must first set `azd` environment variables _before_ running `azd up`.

Run the following commands based on what you want to customize. These are stored in .azure/{environmentName}/.env

* `azd env set AZURE_LOCATION {Location you'd like to use}`
* `azd env set AZURE_OPENAI_RESOURCE {Name of existing OpenAI service}`
* `azd env set AZURE_OPENAI_RESOURCE_GROUP {Name of existing resource group that OpenAI service is provisioned to}`
* `azd env set AZURE_OPENAI_SKU_NAME {Name of OpenAI SKU}`. Defaults to 'S0'.
* `azd env set AZURE_SEARCH_SERVICE {Name of existing Cognitive Search service}`
* `azd env set AZURE_SEARCH_SERVICE_RESOURCE_GROUP {Name of existing resource group that Cognitive Search service is provisioned to}`
* `azd env set AZURE_SEARCH_SKU_NAME {Name of Cognitive Search SKY}`. Defaults to 'standard'.
* `azd env set AZURE_FORMRECOGNIZER_SERVICE {Name of existing Form Recognizer service}`. Used by prepdocs.py for text extraction from docs.
* `azd env set AZURE_FORMRECOGNIZER_SERVICE_RESOURCE_GROUP {Name of existing resource group that Form Recognizer service is provisioned to}`.
* `azd env set AZURE_FORMRECOGNIZER_SKU_NAME {Name of Form Recognizer SKU}`. Defaults to 'S0'.

1. Run `azd auth login` to login to your Azure account.
1. Run `azd up` to provision Azure resources and deploy this sample to those resources. This also runs a script to build the search index based on files in the `./data` folder.
1. After the application has been successfully deployed you will see two URLs printed to the console.  Click the web URL to interact with the application in your browser.
    > NOTE: It may take a minute for the application to be fully deployed. If you see a "Python Developer" welcome screen, then wait a minute and refresh the page.

The deployment process will look similar to the following:
```
PS C:\> azd up
Note: Running custom 'up' workflow from azure.yaml

Provisioning Azure resources (azd provision)
Provisioning Azure resources can take some time.

Subscription: YOUR-SUB-NAME (00000000-0000-0000-0000-000000000000)
Location: East US 2

Deploying services (azd deploy)
  (✓) Done: Resource group: rg-chiron
  (✓) Done: Storage account: stabc123xyz789
  (✓) Done: Azure OpenAI: chrion-aoai
  (✓) Done: App Service plan: plan-abc123xyz789
  (✓) Done: Storage account: stabc123xyz789
  (✓) Done: Azure OpenAI: chrion-aoai
  (✓) Done: App Service plan: plan-abc123xyz789
  (✓) Done: App Service plan: plan-abc123xyz789
  (✓) Done: Static Web App: stapp-frontend-abc123xyz789
  (✓) Done: Function App: app-api-abc123xyz789

Deploying services (azd deploy)

  (✓) Done: Deploying service api
  - Endpoint: https://app-api-xyz.azurewebsites.net/

  (✓) Done: Deploying service web
  - Endpoint: https://adjective-noun-xyz.azurestaticapps.net/

SUCCESS: Your up workflow to provision and deploy to Azure completed in X minutes Y seconds
```
### Re-deploying changes

If you make any changes to the app code (JS or Python), you can re-deploy the app code to App Service by running the `azd deploy` command.

If you change any of the Bicep files in the infra folder, then you should re-run `azd up` to both provision resources and deploy code.

### Running locally:

See [the main README](./README.md) ***Getting Started*** section.

### Note

>Note: The PDF documents used in this demo contain information generated using a language model (Azure OpenAI Service). The information contained in these documents is only for demonstration purposes and does not reflect the opinions or beliefs of Microsoft. Microsoft makes no representations or warranties of any kind, express or implied, about the completeness, accuracy, reliability, suitability or availability with respect to the information contained in this document. All rights reserved to Microsoft.
