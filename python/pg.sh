#!/bin/bash

# Bash script to connect to your Azure PostgreSQL server
# per your AIG4PG_PG_FLEX_xxx environment variables. 
#
# Note: On macOS, with a local installation of PostgreSQL 17
# with 'brew install postgresql@17', the psql CLI program
# name is 'psql-17' as shown below.
#
# Chris Joakim, 3Cloud

export AIG4PG_PG_FLEX_DB=dev

export PGHOST=$AIG4PG_PG_FLEX_SERVER
export PGUSER=$AIG4PG_PG_FLEX_USER
export PGPORT=$AIG4PG_PG_FLEX_PORT
export PGDATABASE=$AIG4PG_PG_FLEX_DB
export PGPASSWORD=$AIG4PG_PG_FLEX_PASS

psql-17
