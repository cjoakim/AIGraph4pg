#!/bin/bash

# Bash script to dump a PostgreSQL database, both with
# the --schema-only and --data-only args.
# Assumes that you have pg_dump installed on your computer.
# Edit the generated values per your actual deployments.

server=$AIG4PG_PG_FLEX_SERVER
port=$AIG4PG_PG_FLEX_PORT
user=$AIG4PG_PG_FLEX_USER
db='dev'

mkdir -p tmp

env | grep AIG4PG_PG_FLEX_PASS

echo 'dumping the --schema-only, enter password...'
pg_dump --schema-only --host $server --port $port --username $user --format plain --verbose --file 'tmp/pg_dump_schema.sql' --dbname $db

echo 'dumping the --data-only, enter password...'
pg_dump --data-only --host $server --port $port --username $user --format plain --verbose --file 'tmp/pg_dump_data.sql' --dbname $db

echo 'list of tmp files:'
ls tmp
