# AI Project/Hub and Key Vault resources

data "azurerm_client_config" "current" {}

resource "azurerm_storage_account" "ai_hub" {
  name                     = "${var.environment_name}aihubsa"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  min_tls_version          = "TLS1_2"
  tags                     = var.tags
}

resource "azurerm_key_vault" "ai_hub" {
  name                            = "${var.environment_name}-aihub-kv"
  location                        = azurerm_resource_group.main.location
  resource_group_name             = azurerm_resource_group.main.name
  tenant_id                       = data.azurerm_client_config.current.tenant_id
  sku_name                        = "standard"
  purge_protection_enabled        = false
  enabled_for_deployment          = true
  enabled_for_disk_encryption     = true
  enabled_for_template_deployment = true
  tags                            = var.tags
}

resource "azurerm_machine_learning_workspace" "ai_hub" {
  name                = "${var.environment_name}-aihub"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  friendly_name       = "AI Hub for Snippy code analysis"
  description         = "AI Hub for Snippy code analysis"
  identity {
    type = "SystemAssigned"
  }
  key_vault_id            = azurerm_key_vault.ai_hub.id
  storage_account_id      = azurerm_storage_account.ai_hub.id
  application_insights_id = azurerm_application_insights.main.id
  tags                    = var.tags
}

resource "azurerm_machine_learning_workspace" "ai_project" {
  name                    = "${var.environment_name}-aiproject"
  location                = azurerm_resource_group.main.location
  resource_group_name     = azurerm_resource_group.main.name
  application_insights_id = azurerm_application_insights.main.id
  storage_account_id      = azurerm_storage_account.ai_hub.id
  key_vault_id            = azurerm_key_vault.ai_hub.id
  friendly_name           = "AI Project for Snippy code analysis"
  description             = "AI Project for Snippy code analysis"
  identity {
    type = "SystemAssigned"
  }
  tags = merge(var.tags, {
    ProjectConnectionString = "${var.location}.api.azureml.ms;${data.azurerm_client_config.current.subscription_id};${azurerm_resource_group.main.name};${var.environment_name}-aiproject"
  })
  depends_on = [azurerm_machine_learning_workspace.ai_hub]
}

# Role assignments for AI Project to access AI Services
resource "azurerm_role_assignment" "cognitive_services_contributor" {
  scope                = azurerm_cognitive_account.main.id
  role_definition_name = "Cognitive Services Contributor"
  principal_id         = azurerm_machine_learning_workspace.ai_project.identity[0].principal_id
}

resource "azurerm_role_assignment" "cognitive_services_openai_user" {
  scope                = azurerm_cognitive_account.main.id
  role_definition_name = "Cognitive Services OpenAI User"
  principal_id         = azurerm_machine_learning_workspace.ai_project.identity[0].principal_id
}

resource "azurerm_role_assignment" "cognitive_services_user" {
  scope                = azurerm_cognitive_account.main.id
  role_definition_name = "Cognitive Services User"
  principal_id         = azurerm_machine_learning_workspace.ai_project.identity[0].principal_id
}