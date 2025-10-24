# Random suffix for storage account name
resource "random_string" "storage_suffix" {
  length  = 6
  special = false
  upper   = false
}

# Storage Account for backups and diagnostics
resource "azurerm_storage_account" "main" {
  name                     = "${replace(var.app_name, "-", "")}st${random_string.storage_suffix.result}"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "GRS"
  https_traffic_only_enabled = true
  min_tls_version          = "TLS1_2"

  identity {
    type = "SystemAssigned"
  }

  tags = merge(local.common_tags, var.tags)
}

# Storage Account Encryption
resource "azurerm_storage_account_customer_managed_key" "main" {
  storage_account_id = azurerm_storage_account.main.id
  key_vault_id       = azurerm_key_vault.main.id
  key_name           = azurerm_key_vault_key.storage_key.name
}

# Key Vault Key for Storage Encryption
resource "azurerm_key_vault_key" "storage_key" {
  name            = "storage-encryption-key"
  key_vault_id    = azurerm_key_vault.main.id
  key_type        = "RSA"
  key_size        = 4096
  key_opts        = ["decrypt", "encrypt", "sign", "unwrapKey", "verify", "wrapKey"]
  expiration_date = timeadd(timestamp(), "8760h") # 1 year

  tags = merge(local.common_tags, var.tags)
}

# Storage Container for Database Backups
resource "azurerm_storage_container" "db_backups" {
  name                  = "database-backups"
  storage_account_id    = azurerm_storage_account.main.id
  container_access_type = "private"
}

# Storage Container for Diagnostic Logs
resource "azurerm_storage_container" "diagnostic_logs" {
  name                  = "diagnostic-logs"
  storage_account_id    = azurerm_storage_account.main.id
  container_access_type = "private"
}

# Diagnostic Setting for PostgreSQL Logs to Storage
resource "azurerm_monitor_diagnostic_setting" "postgresql_storage" {
  name               = "${var.app_name}-db-diagnostic-setting"
  target_resource_id = azurerm_postgresql_flexible_server.main.id
  storage_account_id = azurerm_storage_account.main.id

  enabled_log {
    category = "PostgreSQLLogs"
  }
}

# Storage Account Lifecycle Management for backups
resource "azurerm_storage_management_policy" "main" {
  storage_account_id = azurerm_storage_account.main.id

  rule {
    name    = "DeleteOldBackups"
    enabled = true
    filters {
      blob_types   = ["blockBlob"]
      prefix_match = ["database-backups/"]
    }
    actions {
      base_blob {
        delete_after_days_since_modification_greater_than = 90
      }
    }
  }

  depends_on = [azurerm_storage_container.db_backups]
}

# RBAC role for Container Apps to access storage
resource "azurerm_role_assignment" "container_apps_storage" {
  scope              = azurerm_storage_account.main.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id       = azurerm_user_assigned_identity.container_apps.principal_id

  depends_on = [azurerm_user_assigned_identity.container_apps]
}
