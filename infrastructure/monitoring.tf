# Application Insights for app monitoring
resource "azurerm_application_insights" "main" {
  name                = "${var.app_name}-appinsights-${random_string.kv_suffix.result}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  application_type    = "web"
  workspace_id        = azurerm_log_analytics_workspace.main.id

  tags = merge(local.common_tags, var.tags)
}

# Diagnostic setting for Container App to Application Insights
resource "azurerm_monitor_diagnostic_setting" "container_app" {
  name               = "${var.app_name}-app-diagnostic-setting"
  target_resource_id = azurerm_container_app.main.id
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id

  enabled_log {
    category = "ContainerAppSystemLogs"
  }

  enabled_log {
    category = "ContainerAppConsoleLogs"
  }
}

# Diagnostic setting for Container Registry
resource "azurerm_monitor_diagnostic_setting" "container_registry" {
  name               = "${var.app_name}-acr-diagnostic-setting"
  target_resource_id = azurerm_container_registry.main.id
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id

  enabled_log {
    category = "ContainerRegistryRepositoryEvents"
  }

  enabled_log {
    category = "ContainerRegistryLoginEvents"
  }
}

# Alert for Container App CPU High
resource "azurerm_monitor_metric_alert" "cpu_high" {
  name                = "${var.app_name}-cpu-high-alert"
  resource_group_name = azurerm_resource_group.main.name
  scopes              = [azurerm_container_app.main.id]
  description         = "Alert when CPU usage is high"
  frequency           = "PT1M"
  window_size         = "PT5M"

  criteria {
    metric_name            = "CpuUsagePercentage"
    metric_namespace       = "Microsoft.App/containerApps"
    aggregation            = "Average"
    operator               = "GreaterThan"
    threshold              = 80
    skip_metric_validation = false
  }

  action {
    action_group_id = azurerm_monitor_action_group.main.id
  }
}

# Alert for Container App Memory High
resource "azurerm_monitor_metric_alert" "memory_high" {
  name                = "${var.app_name}-memory-high-alert"
  resource_group_name = azurerm_resource_group.main.name
  scopes              = [azurerm_container_app.main.id]
  description         = "Alert when memory usage is high"
  frequency           = "PT1M"
  window_size         = "PT5M"

  criteria {
    metric_name            = "MemoryUsagePercentage"
    metric_namespace       = "Microsoft.App/containerApps"
    aggregation            = "Average"
    operator               = "GreaterThan"
    threshold              = 80
    skip_metric_validation = false
  }

  action {
    action_group_id = azurerm_monitor_action_group.main.id
  }
}

# Alert for Database Connection Failures
resource "azurerm_monitor_metric_alert" "db_failed_connections" {
  name                = "${var.app_name}-db-failed-connections-alert"
  resource_group_name = azurerm_resource_group.main.name
  scopes              = [azurerm_postgresql_flexible_server.main.id]
  description         = "Alert on database connection failures"
  frequency           = "PT1M"
  window_size         = "PT5M"

  criteria {
    metric_name            = "active_connections"
    metric_namespace       = "Microsoft.DBforPostgreSQL/flexibleServers"
    aggregation            = "Average"
    operator               = "LessThan"
    threshold              = 1
    skip_metric_validation = false
  }

  action {
    action_group_id = azurerm_monitor_action_group.main.id
  }
}

# Alert for Database Storage High
resource "azurerm_monitor_metric_alert" "db_storage_high" {
  name                = "${var.app_name}-db-storage-high-alert"
  resource_group_name = azurerm_resource_group.main.name
  scopes              = [azurerm_postgresql_flexible_server.main.id]
  description         = "Alert when database storage is high"
  frequency           = "PT5M"
  window_size         = "PT15M"

  criteria {
    metric_name            = "storage_percent"
    metric_namespace       = "Microsoft.DBforPostgreSQL/flexibleServers"
    aggregation            = "Average"
    operator               = "GreaterThan"
    threshold              = 80
    skip_metric_validation = false
  }

  action {
    action_group_id = azurerm_monitor_action_group.main.id
  }
}

# Action Group for Alerts (Email notifications)
resource "azurerm_monitor_action_group" "main" {
  name                = "${var.app_name}-action-group"
  resource_group_name = azurerm_resource_group.main.name
  short_name          = "BankApp"

  tags = merge(local.common_tags, var.tags)
}

# Alert for HTTP Request Failures (5xx)
resource "azurerm_monitor_scheduled_query_rules_alert" "http_5xx_errors" {
  name                = "${var.app_name}-http-5xx-errors"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location

  data_source_id = azurerm_log_analytics_workspace.main.id

  query       = "AppRequests | where ResultCode >= 500 | summarize Count = count() by ResultCode"
  frequency   = "PT5M"
  time_window = "PT15M"
  trigger {
    operator  = "GreaterThan"
    threshold = 10
  }

  action {
    action_group = azurerm_monitor_action_group.main.id
  }

  enabled = true
  description = "Alert on HTTP 5xx errors in application"
}

# Query for Application Performance (KQL)
resource "azurerm_log_analytics_query_pack_query" "app_performance" {
  query_pack_id   = azurerm_log_analytics_query_pack.main.id
  body            = "AppRequests | summarize Count = count(), AvgDuration = avg(DurationMs) by Name | order by Count desc"
  display_name    = "Application Performance"
  description     = "Average response time and request count by endpoint"
  tags            = merge(local.common_tags, var.tags)
}

# Query for Error Rate Analysis
resource "azurerm_log_analytics_query_pack_query" "error_rate" {
  query_pack_id   = azurerm_log_analytics_query_pack.main.id
  body            = "AppRequests | summarize TotalCount = count(), FailureCount = sum(iff(Success == false, 1, 0)), FailureRate = tostring(sum(iff(Success == false, 1, 0)) * 100.0 / count()) by Name"
  display_name    = "Error Rate Analysis"
  description     = "Failure count and error rate by endpoint"
  tags            = merge(local.common_tags, var.tags)
}

# Query for Database Performance
resource "azurerm_log_analytics_query_pack_query" "db_performance" {
  query_pack_id   = azurerm_log_analytics_query_pack.main.id
  body            = "AzureDiagnostics | where ResourceType == 'SERVERS' | summarize AvgDuration = avg(duration_t), MaxDuration = max(duration_t), Count = count() by Database"
  display_name    = "Database Performance"
  description     = "Query performance metrics by database"
  tags            = merge(local.common_tags, var.tags)
}

# Query Pack for custom monitoring queries
resource "azurerm_log_analytics_query_pack" "main" {
  name                = "${var.app_name}-query-pack"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location

  tags = merge(local.common_tags, var.tags)
}
