[![Build Status](https://travis-ci.org/diegovalle/hoyodecrimen.api.svg?branch=master)](https://travis-ci.org/diegovalle/hoyodecrimen.api)

Distrito Federal Crime API and Website
===========================

You'll need to set the following environmental variables for the testing environment:

```
OPENSHIFT_POSTGRESQL_DB_PASSWORD=""
OPENSHIFT_POSTGRESQL_DB_URL="postgresql://x:x@localhost/apihoyodecrimen"
REDIS_PASSWORD=""
OPENSHIFT_REDIS_HOST='127.0.0.1'
OPENSHIFT_REDIS_PORT='6379'
OPENSHIFT_APP_UUID=true (only when running in production)
```

To deploy to a server use the ansible script in the ansible directory.

*Updating*

To update the carto table you first have to delete all rows in the existing table

```sql
TRUNCATE TABLE crime_lat_long
```

and then upload the new table to a tempory one and copy all rows to crime_lat_long

```sql
INSERT INTO crime_lat_long SELECT * FROM crime_lat_long_1
```

and then delete the temporary table

```
psql -d apihoyodecrimen -U $OPENSHIFT_POSTGRESQL_DB_USERNAME -W  -c ""
```
