param name string
param location string = resourceGroup().location
param tags object = {}

param serviceName string = 'web'
param appServiceName string

module web '../core/host/staticwebapp.bicep' = {
  name: '${serviceName}-staticwebapp-module'
  params: {
    name: name
    location: location
    tags: union(tags, { 'azd-service-name': serviceName })
    appServiceName: appServiceName
  }
}

output SERVICE_WEB_NAME string = web.outputs.name
output SERVICE_WEB_URI string = web.outputs.uri
