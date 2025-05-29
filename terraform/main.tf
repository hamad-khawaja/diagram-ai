resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name != null ? var.resource_group_name : "rg-${var.environment_name}"
  location = var.location
  tags     = var.tags
}

# Call the function_app module for the MCP/API endpoint
module "function_app" {
  source                                 = "./funtion_app"
  function_app_name                      = "architecture-diagram-generator-${var.environment_name}"
  app_service_plan_name                  = "asp-${var.environment_name}"
  application_insights_id                = azurerm_application_insights.main.id
  application_insights_connection_string = azurerm_application_insights.main.connection_string
  tags                                   = var.tags
  environment_name                       = var.environment_name
  resource_group_name                    = azurerm_resource_group.main.name
  location                               = var.location
  #   identity_client_id                         = var.identity_client_id
  azure_openai_key = var.azure_openai_key
  # Add any additional variables needed for advanced configuration (e.g., VNET, deployment container, etc.)
}
