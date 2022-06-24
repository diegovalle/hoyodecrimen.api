[![Build Status](https://travis-ci.org/diegovalle/hoyodecrimen.api.svg?branch=master)](https://travis-ci.org/diegovalle/hoyodecrimen.api)
[![Build Status](https://circleci.com/gh/diegovalle/hoyodecrimen.api.png?style=shield&circle-token=:circle-token)](https://circleci.com/gh/diegovalle/hoyodecrimen.api)

# Distrito Federal Crime API and Website

You'll need to set the following environmental variables for the testing environment:

```
MODULE_NAME
LOG_LEVEL
PORT
SQLALCHEMY_DATABASE_URI
SENTRY_DSN
CACHE_SECRET
```

## To deploy a testing server you have to:

* create a postgresql database called apihoyodecrimen
* Enale the postgis extension ```CREATE EXTENSION IF NOT EXISTS postgis;```
* use the db.sql file in the ansible/roles/hoyodecrimen.app/files to create the tables (be sure to uncomment the lines to
also copy the data)
* copy the cuadrantes polygons ```psql -d apihoyodecrimen < data/cuadrantes_poly.sql```
* add the indexes in the file ansible/roles/hoyodecrimen.app/files/index.sql



## To deploy to a server use the ansible script in the ansible directory.


## Updating

Copy the crime-lat-long, cuadrantes and pgj csv files to the tmp directory
and then run the `update.sh` script.

To update the carto table you first have to delete all rows in the existing table (don't delete the crime_lat_long1 table visualization)

```sql
TRUNCATE TABLE crime_lat_long;
```

and then upload the new table to a tempory one and copy all rows to crime_lat_long

```sql
INSERT INTO crime_lat_long SELECT * FROM crime_lat_long_pgj
WHERE ROWNUM <= 100;
```

and then delete the temporary table

BE SURE THE TABLE IS CALLED crime_lat_long

# Mailing list

Hoyodecrimen Notificaciones:
https://hoyodecrimen.us6.list-manage.com/subscribe/post?u=787fae824c502d9f3ad7d0b73&amp;id=99835eea14

Hoyodecrimen Notifications:
https://hoyodecrimen.us6.list-manage.com/subscribe/post?u=787fae824c502d9f3ad7d0b73&amp;id=102491489b
