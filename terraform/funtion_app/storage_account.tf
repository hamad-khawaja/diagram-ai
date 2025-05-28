resource "azurerm_storage_container" "function_deploy" {
  name                  = "function-deploy"
  storage_account_id    = azurerm_storage_account.function.id
  container_access_type = "private"
}

resource "azurerm_storage_account" "function" {
  name                          = var.storage_account_name
  resource_group_name           = var.resource_group_name
  public_network_access_enabled = true
  location                      = var.location
  account_tier                  = "Standard"
  account_replication_type      = "LRS"
  min_tls_version               = "TLS1_2"

  network_rules {
    bypass         = ["AzureServices"]
    default_action = "Allow"
  }

  tags = var.tags
}

resource "azurerm_storage_blob" "function_package" {
  name                   = "functionapp.zip"
  storage_account_name   = azurerm_storage_account.function.name
  storage_container_name = azurerm_storage_container.function_deploy.name
  type                   = "Block"
  source                 = data.archive_file.function_app_zip.output_path
}

data "azurerm_storage_account_sas" "function_package_sas" {
  connection_string = azurerm_storage_account.function.primary_connection_string
  https_only        = true
  signed_version    = "2022-11-02"

  resource_types {
    service   = true
    container = true
    object    = true
  }

  services {
    blob  = true
    queue = false
    table = false
    file  = false
  }

  start  = "2025-01-01T00:00:00Z"
  expiry = "2030-01-01T00:00:00Z"

  permissions {
    read    = true
    write   = false
    delete  = false
    list    = true
    add     = false
    create  = false
    update  = false
    process = false
    tag     = false
    filter  = false
  }
}