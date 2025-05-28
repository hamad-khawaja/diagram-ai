locals {
  function_package_url = "https://${azurerm_storage_account.function.name}.blob.core.windows.net/${azurerm_storage_container.function_deploy.name}/${azurerm_storage_blob.function_package.name}${data.azurerm_storage_account_sas.function_package_sas.sas}"
}

resource "azurerm_app_service_plan" "function" {
  name                = var.app_service_plan_name != null ? var.app_service_plan_name : "asp-${var.environment_name}"
  location            = var.location
  resource_group_name = var.resource_group_name
  kind                = "FunctionApp"
  reserved            = true
  sku {
    tier = "Dynamic"
    size = "Y1"
  }
}

data "archive_file" "function_app_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../../src"
  output_path = "${path.module}/functionapp.zip"
}


resource "azurerm_linux_function_app" "main" {
  name                        = var.function_app_name
  location                    = var.location
  resource_group_name         = var.resource_group_name
  service_plan_id             = azurerm_app_service_plan.function.id
  storage_account_name        = azurerm_storage_account.function.name
  storage_account_access_key  = azurerm_storage_account.function.primary_access_key
  https_only                  = true
  functions_extension_version = "~4"
  # virtual_network_subnet_id   = azurerm_subnet.function_app_subnet.id
  app_settings = {
    FUNCTIONS_WORKER_RUNTIME              = "python"
    AzureWebJobsStorage                   = azurerm_storage_account.function.primary_connection_string
    WEBSITE_RUN_FROM_PACKAGE              = local.function_package_url
    APPLICATIONINSIGHTS_CONNECTION_STRING = var.application_insights_connection_string
    AzureWebJobsStorage__blobServiceUri   = azurerm_storage_account.function.primary_blob_endpoint
    AzureWebJobsStorage__queueServiceUri  = azurerm_storage_account.function.primary_queue_endpoint
    AzureWebJobsStorage__tableServiceUri  = azurerm_storage_account.function.primary_table_endpoint
    AzureWebJobsStorage__credential       = "managedidentity"
    AzureWebJobsFeatureFlags              = "EnableWorkerIndexing"
    AZURE_OPENAI_KEY                      = var.azure_openai_key
    PYTHON_ENABLE_WORKER_EXTENSIONS       = "1"
  }
  site_config {
    always_on = false
  }
  identity {
    type = "SystemAssigned"
  }
  tags = var.tags
}