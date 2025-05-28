# Terraform equivalent of infra/app/ai/cognitive-services.bicep
# Cognitive Services account for AI models

resource "azurerm_cognitive_account" "main" {
  name                          = "${var.environment_name}-cogsvc"
  location                      = azurerm_resource_group.main.location
  resource_group_name           = azurerm_resource_group.main.name
  public_network_access_enabled = false
  kind                          = "CognitiveServices"
  sku_name                      = "S0"
  identity {
    type = "SystemAssigned"
  }
  tags = var.tags
}
