targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name of the the environment which is used to generate a short unique hash used in all resources.')
param environmentName string

@minLength(1)
@description('Primary location for all resources')
@allowed(['eastus2'])   // The only US region where all resources (including SWAs are available)
param location string

param appServicePlanName string = ''
param apiServiceName string = ''
param apiStorageAccountName string = ''
param frontendServiceName string = ''

@description('Feature flag to enable use of supervisor agent for OpenAI')
param useSupervisor bool = true

param resourceGroupName string = ''

param openAiResourceName string = ''
param openAiResourceGroupName string = ''
param openAiResourceGroupLocation string = location
param openAiSkuName string = ''
param openAIDeploymentName string = 'chat'
param openAIModelName string = 'gpt-4o'
param embeddingDeploymentName string = 'embedding'
param embeddingModelName string = 'text-embedding-ada-002'

@description('Id of the user or app to assign application roles')
param principalId string = ''

var abbrs = loadJsonContent('abbreviations.json')
var resourceToken = toLower(uniqueString(subscription().id, environmentName, location))
var tags = { 'azd-env-name': environmentName }

// Organize resources in a resource group
resource resourceGroup 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: !empty(resourceGroupName) ? resourceGroupName : '${abbrs.resourcesResourceGroups}${environmentName}'
  location: location
  tags: tags
}

resource openAiResourceGroup 'Microsoft.Resources/resourceGroups@2021-04-01' existing = if (!empty(openAiResourceGroupName)) {
  name: !empty(openAiResourceGroupName) ? openAiResourceGroupName : resourceGroup.name
}

// Create an App Service Plan to group applications under the same payment plan and SKU
module appServicePlan 'core/host/appserviceplan.bicep' = {
  name: 'appserviceplan'
  scope: resourceGroup
  params: {
    name: !empty(appServicePlanName) ? appServicePlanName : '${abbrs.webServerFarms}${resourceToken}'
    location: location
    tags: tags
    sku: {
      name: 'Y1'
      tier: 'Dynamic'
    }
  }
}

// The application api
var appServiceName = !empty(apiServiceName) ? apiServiceName : '${abbrs.webSitesAppService}api-${resourceToken}'
var storageAccountName = !empty(apiStorageAccountName) ? apiStorageAccountName : '${abbrs.storageStorageAccounts}${resourceToken}'

module storageAccount 'core/storage/storage-account.bicep' = {
  name: 'storageaccount'
  scope: resourceGroup
  params: {
    name: storageAccountName
    location: location
  }
}

module api 'app/api.bicep' = {
  name: 'functionapp'
  scope: resourceGroup
  params: {
    name: appServiceName
    location: location
    tags: union(tags, { 'azd-service-name': 'api' })
    appServicePlanId: appServicePlan.outputs.id
    storageAccountName: storageAccount.outputs.name
    keyVaultName: ''
    managedIdentity: true
    appSettings: {
      AzureWebJobsFeatureFlags: 'EnableWorkerIndexing'
      // openai
      AZURE_OPENAI_ENDPOINT: openAi.outputs.name
      AZURE_OPENAI_API_KEY: openAi.outputs.key
      AZURE_OPENAI_API_VERSION: '2024-02-15-preview'
      AZURE_OPENAI_API_DEPLOYMENT_NAME: openAIDeploymentName
      USE_SUPERVISOR: useSupervisor
    }
  }
}

var staticAppServiceName = !empty(frontendServiceName) ? frontendServiceName : '${abbrs.webStaticSites}frontend-${resourceToken}'
module web 'app/web.bicep' = {
  name: 'frontend'
  scope: resourceGroup
  params: {
    name: staticAppServiceName
    location: location
    appServiceName: appServiceName

  }
}

module openAi 'core/ai/cognitiveservices.bicep' = {
  name: 'openai'
  scope: openAiResourceGroup
  params: {
    name: !empty(openAiResourceName) ? openAiResourceName : '${abbrs.cognitiveServicesAccounts}${resourceToken}'
    location: openAiResourceGroupLocation
    tags: tags
    sku: {
      name: !empty(openAiSkuName) ? openAiSkuName : 'S0'
    }
    deployments: [
      {
        name: openAIDeploymentName
        model: {
          format: 'OpenAI'
          name: openAIModelName
          version: '2024-05-13'
        }
        capacity: 30
      }
      {
        name: embeddingDeploymentName
        model: {
          format: 'OpenAI'
          name: embeddingModelName
          version: '2'
        }
        capacity: 30
      }
    ]
  }
}


// USER ROLES
module openAiRoleUser 'core/security/role.bicep' = {
  scope: openAiResourceGroup
  name: 'openai-role-user'
  params: {
    principalId: principalId
    roleDefinitionId: '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd'
    principalType: 'User'
  }
}

// // SYSTEM IDENTITIES
module openAiRoleBackend 'core/security/role.bicep' = {
  scope: openAiResourceGroup
  name: 'openai-role-backend'
  params: {
    principalId: api.outputs.SERVICE_API_IDENTITY_PRINCIPAL_ID
    roleDefinitionId: '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd'
    principalType: 'ServicePrincipal'
  }
}

output AZURE_LOCATION string = location
output AZURE_TENANT_ID string = tenant().tenantId
output AZURE_RESOURCE_GROUP string = resourceGroup.name

output BACKEND_URI string = api.outputs.SERVICE_API_URI

// openai
output AZURE_OPENAI_ENDPOINT string = openAi.outputs.endpoint
output AZURE_OPENAI_API_DEPLOYMENT_NAME string = openAIDeploymentName
output AZURE_OPENAI_MODEL_NAME string = openAIModelName
output AZURE_OPENAI_EMBEDDING_NAME string = embeddingDeploymentName
output USE_SUPERVISOR bool = useSupervisor
