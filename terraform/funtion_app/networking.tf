
# # Networking resources for VNET integration
# resource "azurerm_virtual_network" "function_app_vnet" {
#   name                = "${var.environment_name}-func-vnet"
#   address_space       = ["10.10.0.0/16"]
#   location            = var.location
#   resource_group_name = var.resource_group_name
#   tags                = var.tags
# }

# resource "azurerm_subnet" "function_app_subnet" {
#   name                 = "${var.environment_name}-func-subnet"
#   resource_group_name  = var.resource_group_name
#   virtual_network_name = azurerm_virtual_network.function_app_vnet.name
#   address_prefixes     = ["10.10.1.0/24"]
#   service_endpoints    = ["Microsoft.Storage"]
# }

# resource "azurerm_subnet_delegation" "function_app" {
#   name      = "functionapp-delegation"
#   subnet_id = azurerm_subnet.function_app_subnet.id
#   service_delegation {
#     name = "Microsoft.Web/serverFarms"
#     actions = [
#       "Microsoft.Network/virtualNetworks/subnets/action"
#     ]
#   }
# }