# PowerShell script to dump a PostgreSQL database, both with
# the --schema-only and --data-only args.
# Assumes that you have pg_dump installed on your computer.
# Edit the generated values per your actual deployments.

$server=$Env:AIG4PG_PG_FLEX_SERVER
$port=$Env:AIG4PG_PG_FLEX_PORT
$user=$Env:AIG4PG_PG_FLEX_USER
$db='dev'

if (-not (Test-Path -Path .\tmp)) {
 New-Item -ItemType Directory -Path .\tmp
}
Set-Clipboard -value $Env:AIG4PG_PG_FLEX_PASS

Write-Host 'dumping the --schema-only, enter password...'
pg_dump --schema-only --host $server --port $port --username $user --format plain --verbose --file 'tmp\pg_dump_schema.sql' --dbname $db

Write-Host 'dumping the --data-only, enter password...'
pg_dump --data-only --host $server --port $port --username $user --format plain --verbose --file 'tmp\pg_dump_data.sql' --dbname $db

Set-Clipboard -value 'done'

Write-Host 'list of tmp files:'
Get-ChildItem tmp
