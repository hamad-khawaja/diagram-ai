variable "environment_name" {
  description = "Name of the environment which is used to generate a short unique hash used in all resources."
  type        = string
  default     = "dev"
}

variable "location" {
  description = "Primary location for all resources"
  type        = string
  default     = "centralus"
}

variable "resource_group_name" {
  description = "Name of the resource group."
  type        = string
  default     = "diagram-ai"
}

variable "tags" {
  description = "Tags to apply to resources."
  type        = map(string)
  default     = {}
}

variable "azure_openai_key" {
  description = "Azure OpenAI key for the Function App."
  type        = string
  default     = ""
}


