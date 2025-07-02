#!/bin/bash

# Provisions an Azure PostgreSQL Server using the Azure CLI.
# See https://learn.microsoft.com/en-us/cli/azure/get-started-with-azure-cli
# Chris Joakim, Microsoft

mkdir -p tmp
json_data=$(cat provision-config.json)
echo $json_data

azure_subscription=$(echo "$json_data" | jq -r '.azure_subscription')
azure_region=$(echo "$json_data" | jq -r '.azure_region')
resource_group=$(echo "$json_data" | jq -r '.resource_group')
pg_server_name=$(echo "$json_data" | jq -r '.pg_server_name')
pg_sku_name=$(echo "$json_data" | jq -r '.pg_sku_name')
pg_high_availability=$(echo "$json_data" | jq -r '.pg_high_availability')
pg_database_name=$(echo "$json_data" | jq -r '.pg_database_name')
pg_admin_user_name=$(echo "$json_data" | jq -r '.pg_admin_user_name')
pg_admin_user_pass=$(echo "$json_data" | jq -r '.pg_admin_user_pass')
pg_extensions=$(echo "$json_data" | jq -r '.pg_extensions')
az_verbose_flag=$(echo "$json_data" | jq -r '.az_verbose_flag')
my_ip_address=`curl http://ifconfig.me/ip`

echo "azure_subscription:   "$azure_subscription
echo "azure_region:         "$azure_region
echo "pg_server_name:       "$pg_server_name
echo "pg_sku_name:          "$pg_sku_name
echo "pg_high_availability: "$pg_high_availability
echo "pg_database_name:     "$pg_database_name
echo "pg_admin_user_name:   "$pg_admin_user_name
echo "pg_admin_user_pass:   "$pg_admin_user_pass
echo "pg_extensions:        "$pg_extensions
echo "my_ip_address:        "$my_ip_address
echo "az_verbose_flag:      "$az_verbose_flag

#exit 0

echo 'deleting tmp files ...'
rm tmp/*.* 

echo 'az login ...'
az login $az_verbose_flag

echo 'setting subscription ...'
az account set --subscription $az_verbose_flag > ./tmp/account_set.json

echo 'az account show (subscription) ...'
az account show $az_verbose_flag > ./tmp/account_show.json

echo 'az ad signed-in-user show ...'
az ad signed-in-user show $az_verbose_flag > ./tmp/signed_in_user_show.json

echo 'az group create ...'
az group create \
    --name $resource_group \
    --location $azure_region $az_verbose_flag > ./tmp/az_group_create.json

# Version 16 supports AGE, version 17 currently doesn't.

echo 'az postgres flexible-server create ...'
az postgres flexible-server create \
    --subscription $azure_subscription \
    --resource-group $resource_group \
    --name $pg_server_name \
    --sku-name $pg_sku_name \
    --tier GeneralPurpose \
    --version 16 \
    --storage-size 512 \
    --performance-tier P30 \
    --high-availability $pg_high_availability \
    --database-name $pg_database_name \
    --password-auth Enabled \
    --admin-user $pg_admin_user_name \
    --admin-password $pg_admin_user_pass \
    --public-access $my_ip_address $az_verbose_flag > ./tmp/az_pg_flex_create.json

echo 'az postgres flexible-server parameter set ...'
az postgres flexible-server parameter set \
    --resource-group $resource_group \
    --server-name $pg_server_name \
    --subscription $azure_subscription \
    --name azure.extensions \
    --value $pg_extensions $az_verbose_flag > ./tmp/az_pg_flex_enable_extensions.json
