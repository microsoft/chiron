param name string
param location string = resourceGroup().location
param tags object = {}

param allowedOrigins array = []
param applicationInsightsName string = ''
param appServicePlanId string
param appSettings object = {}
param keyVaultName string
param serviceName string = 'api'
param storageAccountName string
param managedIdentity bool = !empty(keyVaultName)

module api '../core/host/functions.bicep' = {
  name: '${serviceName}-functions-python-module'
  params: {
    name: name
    location: location
    tags: union(tags, { 'azd-service-name': serviceName })
    allowedOrigins: allowedOrigins
    alwaysOn: false
    appSettings: appSettings
    applicationInsightsName: applicationInsightsName
    appServicePlanId: appServicePlanId
    keyVaultName: keyVaultName
    managedIdentity: managedIdentity
    //py
    numberOfWorkers: 1
    minimumElasticInstanceCount: 0
    //--py
    runtimeName: 'python'
    runtimeVersion: '3.11'
    storageAccountName: storageAccountName
    scmDoBuildDuringDeployment: false
  }
}

output SERVICE_API_IDENTITY_PRINCIPAL_ID string = api.outputs.identityPrincipalId
output SERVICE_API_NAME string = api.outputs.name
output SERVICE_API_URI string = api.outputs.uri
