# Helper script to execute the psql command-line shell utility.
# It uses your environment variables to determine the host, user,
# and password per a given environment name arg.
#
# This script can be used to connect to a local PostgreSQL server,
# or an Azure PostgreSQL Flex server.
#
# Execute the following command in PowerShell to see script usage:
# (venv) PS ...\python> .\pg.ps1 help
#
# Chris Joakim, 3Cloud

param(
    [Parameter()]
    [String]$env_name  = "",
    [String]$db_name   = "aigraph",
    [String]$psql_file = ""
)

$h=""
$p="5432"
$user="<user>"
$pass="<pass>"
$ssl=""
$win_user=$Env:UserName
$valid_env="false"

if ('local' -eq $env_name) {
    $valid_env="true"
    $h="localhost"
    $user=$win_user
    $pass=$Env:LOCAL_PG_PASS
}
elseif ('flex' -eq $env_name)
{
    $valid_env="true"
    $h=$Env:AIG4PG_PG_FLEX_SERVER
    $user=$Env:AIG4PG_PG_FLEX_USER
    $pass=$Env:AIG4PG_PG_FLEX_PASS
    $ssl="sslmode=require"
}
else {
    Write-Output "unknown env_name $env_name, terminating"
    Write-Output ""
    Write-Output "Usage:"
    Write-Output ".\pg.ps1 <env> <db> where <env> is local or flex"
    Write-Output ".\pg.ps1 local dev"
    Write-Output ".\pg.ps1 flex dev"
    Write-Output ".\pg.ps1 flex dev ..\data\legal_cases\age_load_statments.sql"
    Write-Output ""
    Exit
}

if ('true' -eq $valid_env) {
    if ("" -eq $psql_file) {
        Write-Output "interactive psql - connecting to host: $h, db: $db_name, user: $user"
        if ("nodb" -eq $db_name) {
            $psql_args="host=$h port=$p user=$user password=$pass $ssl"
        }
        else {
            $psql_args="host=$h port=$p dbname=$db_name user=$user password=$pass $ssl"
        }
        psql "$psql_args"
    }
    else {
        Write-Output "batch psql - connecting to host: $h, db: $db_name, user: $user, using file: $psql_file"
        $psql_args="host=$h port=$p dbname=$db_name user=$user password=$pass $ssl"
        psql -f $psql_file "$psql_args"
    }
}
