
output "function_app_name" {
  value = azurerm_linux_function_app.main.name
}

output "function_app_identity_principal_id" {
  value = azurerm_linux_function_app.main.identity[0].principal_id
}
