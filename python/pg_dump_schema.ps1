
# Execute pg_dump to dump a given schema name.
# In this case the script dumps the 'legal_cases' schema
# where the Apache AGE 'legal_cases' graph exists.

$server=$Env:AIG4PG_PG_FLEX_SERVER
$port=$Env:AIG4PG_PG_FLEX_PORT
$user=$Env:AIG4PG_PG_FLEX_USER
$db='dev'
$schema='legal_cases'

if (-not (Test-Path -Path .\tmp\dump)) {
 New-Item -ItemType Directory -Path .\tmp\dump
}
Set-Clipboard -value $Env:AIG4PG_PG_FLEX_PASS

Write-Host 'dumping the --schema-only, enter password...'
pg_dump --schema-only --host $server --port $port --username $user --format plain --verbose --file 'tmp\dump\pg_dump_schema_schema.sql' --dbname $db --schema $schema 

Write-Host 'dumping the --data-only, enter password...'
pg_dump --data-only --host $server --port $port --username $user --format plain --verbose --file 'tmp\dump\pg_dump_schema_data.sql' --dbname $db --schema $schema 

Set-Clipboard -value 'done'

Write-Host 'list of tmp\dump files:'
Get-ChildItem tmp\dump
