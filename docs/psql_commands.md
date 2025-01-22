# AIGraph4pg : Common psql Commands 

You will frequently use these commands in psql.

## psql Commands 

```
command            description
-----------------  ----------------------------------------------
\q                 quit the client program
\l                 list databases
\c dbname          use the given database
\connect dbname    use the given database
\conninfo          display connection info; server, ip, port, db
\copy              see example below
\d                 list tables, or "List of relations"
\d                 show tables
\d customers       describe the customers table
\d+ customers      describe the customers table with details
\det               list foreign tables
\df                list functions
\df *load*         list functions with wildcard
\dn                list schemas
\di                list indexes
\di *lib*          list indexes with wildcard
\dt                show all the tables in db
\dt *.*            show all the tables in system & db
\dT                list of data types
\di                list indexes
\di *libraries*    list indexes with wildcard
\du                list roles
\dv                list views
\dx                list extensions
\?                 show the list of \postgres commands
\h                 show the list of SQL commands (i.e. - help)
\h command         show syntax on this SQL command (i.e. - help)
\pset pager 0      Turn output pagination off
\pset pager 1      Turn output pagination on
\set               list the settings
\set HISTSIZE 600  change a setting value
\timing on|off     Toggle the display of execution ms
\x on              Turn on mysql-like \G output
\x off             Turn off mysql-like \G output
```

See https://quickref.me/postgres.html
