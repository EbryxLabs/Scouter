import argparse

##################################################################################################################################

def MariaDB():
    from MariaDB.azure_maria_db_network_connection import azure_maria_db_network_connection

    azure_maria_db_network_connection()

##################################################################################################################################

def MySQL():
    from MySQL.azure_mysql_network_connection import azure_mysql_network_connection
    from MySQL.azure_mysql_ssl_encrpyted_connection import azure_mysql_ssl_encrpyted_connection

    azure_mysql_network_connection()
    azure_mysql_ssl_encrpyted_connection()

##################################################################################################################################

def PostgreSql():
    from PostgreSql.azure_db_for_postgresql_ad_admin_auth_enabled import azure_db_for_postgresql_ad_admin_auth_enabled
    from PostgreSql.azure_db_for_postgresql_network_connection import azure_db_for_postgresql_network_connection
    from PostgreSql.azure_db_for_postgresql_server_params import azure_db_for_postgresql_server_params

    azure_db_for_postgresql_ad_admin_auth_enabled()
    azure_db_for_postgresql_network_connection()
    azure_db_for_postgresql_server_params()

##################################################################################################################################

def Redis():
    from Redis.azure_redis_cache_secure_connections_enabled import azure_redis_cache_secure_connections_enabled

    azure_redis_cache_secure_connections_enabled()

##################################################################################################################################

def SQL():
    from SQL.azure_sql_db_advanced_threat_protection_enabled import azure_sql_db_advanced_threat_protection_enabled
    from SQL.azure_sql_db_audit_retention_period import azure_sql_db_audit_retention_period
    from SQL.azure_sql_db_data_encryption_on import azure_sql_db_data_encryption_on
    from SQL.azure_sql_db_servers_with_auth_mode_AD import azure_sql_db_servers_with_auth_mode_AD
    from SQL.azure_sql_db_threat_retention_period import azure_sql_db_threat_retention_period
    from SQL.azure_sql_db_vuln_assessment import azure_sql_db_vuln_assessment
    from SQL.azure_sql_managed_instances_auth_mode_AD import azure_sql_managed_instances_auth_mode_AD
    from SQL.azure_sql_managed_instance_vuln_assessment import azure_sql_managed_instance_vuln_assessment
    from SQL.azure_sql_server_advanced_threat_protection_enabled import azure_sql_server_advanced_threat_protection_enabled
    from SQL.azure_sql_server_audit_retention_period import azure_sql_server_audit_retention_period
    from SQL.azure_sql_server_firewall_rules import azure_sql_server_firewall_rules
    from SQL.azure_sql_server_network_connection import azure_sql_server_network_connection
    from SQL.azure_sql_server_threat_retention_period import azure_sql_server_threat_retention_period
    from SQL.azure_sql_server_vuln_assessment import azure_sql_server_vuln_assessment

    azure_sql_db_advanced_threat_protection_enabled()
    azure_sql_db_audit_retention_period()
    azure_sql_db_data_encryption_on()
    azure_sql_db_servers_with_auth_mode_AD()
    azure_sql_db_threat_retention_period()
    azure_sql_db_vuln_assessment()
    azure_sql_managed_instances_auth_mode_AD()
    azure_sql_managed_instance_vuln_assessment()
    azure_sql_server_advanced_threat_protection_enabled()
    azure_sql_server_audit_retention_period()
    azure_sql_server_firewall_rules()
    azure_sql_server_network_connection()
    azure_sql_server_threat_retention_period()
    azure_sql_server_vuln_assessment()

##################################################################################################################################

def Storage():
    from Storage.azure_defender_for_storage_enabled import azure_defender_for_storage_enabled

    azure_defender_for_storage_enabled()

##################################################################################################################################

# MAIN FUNCTION

parser = argparse.ArgumentParser(description="Run selected services")
parser.add_argument("--service", type=str, required=True, help="The name of the service(s) to run")

args = parser.parse_args()
services = args.service.split(",")  # Split the comma-separated service names into a list

for service_name in services:
    if service_name == "MariaDB":
        MariaDB()
    elif service_name == "MySQL":
        MySQL()
    elif service_name == "PostgreSql":
        PostgreSql()
    elif service_name == "Redis":
        Redis()    
    elif service_name == "SQL":
        SQL()
    elif service_name == "Storage":
        Storage()

    else:
        print(f"Unknown service: {service_name}")

##################################################################################################################################