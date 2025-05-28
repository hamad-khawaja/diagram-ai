variable "function_app_name" {
  description = "Name of the Function App."
  type        = string
}

variable "storage_account_name" {
  description = "Name of the Storage Account for the Function App."
  type        = string
}

variable "app_service_plan_name" {
  description = "Name of the App Service Plan."
  type        = string
}

variable "application_insights_id" {
  description = "Resource ID of Application Insights."
  type        = string
}

variable "application_insights_connection_string" {
  description = "connection string ID of Application Insights."
  type        = string
  sensitive   = true
}

# variable "identity_client_id" {
#   description = "Client ID for the managed identity."
#   type        = string
# }

variable "azure_openai_key" {
  description = "Azure OpenAI key for the Function App."
  type        = string
}

variable "tags" {
  description = "Tags to apply to resources."
  type        = map(string)
  default     = {}
}

variable "environment_name" {
  description = "Name of the environment which is used to generate a short unique hash used in all resources."
  type        = string
}

variable "resource_group_name" {
  description = "Name of the resource group."
  type        = string
}

variable "location" {
  description = "Primary location for all resources"
  type        = string
}