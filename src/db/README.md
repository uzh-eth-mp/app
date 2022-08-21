# PostgreSQL database

The `sql` directory contains all init scripts. The default database name is `db`.

## Connecting to the database from command line

1. Download [psql](https://www.postgresql.org/download/)
2. `psql -U user -h localhost -d db` and use the password defined in [.env](.env)

## Connecting to the database using Docker
`docker exec -it app_db_1 psql postgresql://user:postgres@localhost/db`
(see the password and username in [.env](.env))


## Deleting the local data

To delete the local data, just delete `db-data` in this directory.


## Manually testing `db/manager.py` code

To execute `db/manager.py` functions directly on a `db` container without starting producers / consumers:

1. Start the `db` container: `sh etc/scripts/run-dev-db.sh`
2. Edit and run (from a new terminal window) the script: `python etc/scripts/psql_functions.py`
