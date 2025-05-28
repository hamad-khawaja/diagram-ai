# # Terraform equivalent of infra/app/cosmos-db.bicep
# # Cosmos DB account, database, and container

# variable "cosmos_account_name" {
#   description = "Cosmos DB account name"
#   type        = string
# }

# variable "cosmos_database_name" {
#   description = "Database name"
#   type        = string
# }

# variable "cosmos_container_name" {
#   description = "Container name for snippets"
#   type        = string
# }

# resource "azurerm_cosmosdb_account" "main" {
#   name                = var.cosmos_account_name
#   location            = azurerm_resource_group.main.location
#   resource_group_name = azurerm_resource_group.main.name
#   offer_type          = "Standard"
#   kind                = "GlobalDocumentDB"
#   enable_free_tier    = false
#   capabilities {
#     name = "EnableServerless"
#   }
#   capabilities {
#     name = "EnableNoSQLVectorSearch"
#   }
#   geo_location {
#     location          = azurerm_resource_group.main.location
#     failover_priority = 0
#   }
# }

# resource "azurerm_cosmosdb_sql_database" "main" {
#   name                = var.cosmos_database_name
#   resource_group_name = azurerm_resource_group.main.name
#   account_name        = azurerm_cosmosdb_account.main.name
# }

# resource "azurerm_cosmosdb_sql_container" "main" {
#   name                = var.cosmos_container_name
#   resource_group_name = azurerm_resource_group.main.name
#   account_name        = azurerm_cosmosdb_account.main.name
#   database_name       = azurerm_cosmosdb_sql_database.main.name
#   partition_key_path  = "/id"
# }
