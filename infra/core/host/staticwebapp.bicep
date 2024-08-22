param name string
param location string = resourceGroup().location
param tags object = {}

param sku object = {
  name: 'Standard'
  tier: 'Standard'
}
param appServiceName string

resource backend_appservice 'Microsoft.Web/sites@2022-03-01' existing = {
  name: appServiceName
  scope: resourceGroup()
}

resource web 'Microsoft.Web/staticSites@2022-03-01' = {
  name: name
  location: location
  tags: tags
  sku: sku
  properties: {
    provider: 'Custom'
  }


  resource web_backend_functions 'linkedBackends@2022-03-01' = {
    name: 'swamv_backend_functions'
    
    properties: {
      backendResourceId: backend_appservice.id
      region: location
    }
  }  
}


output name string = web.name
output uri string = 'https://${web.properties.defaultHostname}'
