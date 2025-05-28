output "function_app_name" {
  value = module.function_app.function_app_name
}

output "function_app_identity_principal_id" {
  value = module.function_app.function_app_identity_principal_id
}

output "ai_services_name" {
  value = azurerm_cognitive_account.main.name
}

output "ai_services_id" {
  value = azurerm_cognitive_account.main.id
}

output "ai_services_endpoint" {
  value = azurerm_cognitive_account.main.endpoint
}

output "azure_openai_service_endpoint" {
  value = azurerm_cognitive_account.main.endpoint
}

# primaryKey output (secure):
output "ai_services_primary_key" {
  value     = azurerm_cognitive_account.main.primary_access_key
  sensitive = true
}

output "application_insights_name" {
  value = azurerm_application_insights.main.name
}

output "log_analytics_workspace_id" {
  value = azurerm_log_analytics_workspace.main.id
}

output "log_analytics_workspace_name" {
  value = azurerm_log_analytics_workspace.main.name
}

output "ai_hub_id" {
  value = azurerm_machine_learning_workspace.ai_hub.id
}

output "ai_project_id" {
  value = azurerm_machine_learning_workspace.ai_project.id
}

output "ai_project_name" {
  value = azurerm_machine_learning_workspace.ai_project.name
}

output "ai_project_connection_string" {
  value = azurerm_machine_learning_workspace.ai_project.tags["ProjectConnectionString"]
}