# PostgreSQL database

The `sql` directory contains all init scripts. The default database name is `db`.

## Connecting to the database from command line

1. Download [psql](https://www.postgresql.org/download/)
2. `psql -U user -h localhost -d db` and use the password defined in [.env](.env)

## Deleting the local data

To delete the local data, just delete `db-data` in this directory.