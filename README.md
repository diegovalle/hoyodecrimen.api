[![Build Status](https://travis-ci.org/diegovalle/hoyodecrimen.api.svg?branch=master)](https://travis-ci.org/diegovalle/hoyodecrimen.api)
[![Build Status](https://circleci.com/gh/diegovalle/hoyodecrimen.api.png?style=shield&circle-token=:circle-token)](https://circleci.com/gh/diegovalle/hoyodecrimen.api)

#Distrito Federal Crime API and Website

You'll need to set the following environmental variables for the testing environment:

```
OPENSHIFT_POSTGRESQL_DB_PASSWORD=""
OPENSHIFT_POSTGRESQL_DB_URL="postgresql://user:password@localhost/apihoyodecrimen"
REDIS_PASSWORD=""
OPENSHIFT_REDIS_HOST='127.0.0.1'
OPENSHIFT_REDIS_PORT='6379'
OPENSHIFT_APP_UUID=true (only when running in production)
SENTRY_DSN = Your sentry.io dsn
```

##To deploy a testing server you have to:

* create a postgresql database called apihoyodecrimen
* Enale the postgis extension ```CREATE EXTENSION IF NOT EXISTS postgis;```
* use the db.sql file in the ansible/roles/hoyodecrimen.app/files to create the tables (be sure to uncomment the lines to
also copy the data)
* copy the cuadrantes polygons ```psql -d apihoyodecrimen < data/cuadrantes_poly.sql```
* add the indexes in the file ansible/roles/hoyodecrimen.app/files/index.sql



##To deploy to a server use the ansible script in the ansible directory.


##Updating

truncate the tables `psql -d apihoyodecrimen`

```sql
TRUNCATE TABLE  crime_latlong;
TRUNCATE TABLE  cuadrantes;
TRUNCATE TABLE pgj;
```

update the database with new data

```
psql -d apihoyodecrimen -c "\copy cuadrantes (cuadrante,crime,date,count,year,sector,population) from '/tmp/cuadrantes-pgj.csv' with delimiter as ','  NULL AS 'NA' CSV HEADER"
psql -d apihoyodecrimen  -c "\copy crime_latlong  (cuadrante,crime,date,hour,year,month,latitude,longitude,id) from '/tmp/crime-lat-long-pgj.csv' with delimiter as ','  NULL AS 'NA' CSV HEADER"
psql -d apihoyodecrimen -c "\copy pgj (crime,date,count) from '/tmp/pgj.csv' with delimiter as ','  NULL AS 'NA' CSV HEADER"
```

convert to geom the latitude and longitude

```sql
UPDATE crime_latlong SET geom = ST_GeomFromText('POINT(' || longitude || ' ' || latitude || ')',4326);
```



To update the carto table you first have to delete all rows in the existing table (don't delete the crime_lat_long1 table visualization)

```sql
TRUNCATE TABLE crime_lat_long;
```

and then upload the new table to a tempory one and copy all rows to crime_lat_long

```sql
INSERT INTO crime_lat_long SELECT * FROM crime_lat_long_pgj
```

and then delete the temporary table
