#!/bin/bash

# Bash script to dump the PostgreSQL database
# generated by dev.py on Mon Nov 25 10:01:16 2024
# Edit the generated values per your actual deployments.

server=$AIG4PG_PG_FLEX_SERVER
port=$AIG4PG_PG_FLEX_PORT
user=$AIG4PG_PG_FLEX_USER
db='dev'
table='legal_cases'

mkdir -p tmp/dump

env | grep AIG4PG_PG_FLEX_PASS

echo 'dumping the --schema-only, enter password...'
pg_dump --schema-only --host $server --port $port --username $user --format plain --verbose --file 'tmp/dump/pg_dump_legal_cases_schema.sql' --dbname $db --table $table 

echo 'dumping the --data-only, enter password...'
pg_dump --data-only --host $server --port $port --username $user --format plain --verbose --file 'tmp/dump/pg_dump_legal_cases_data.sql' --dbname $db --table $table 

echo 'list of tmp\dump files:'
ls tmp/dump