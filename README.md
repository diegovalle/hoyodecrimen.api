[![Build Status](https://travis-ci.org/diegovalle/hoyodecrimen.api.svg?branch=master)](https://travis-ci.org/diegovalle/hoyodecrimen.api)

Distrito Federal Crime API and Website
===========================

You'll need to set the following environmental variables:

```
OPENSHIFT_POSTGRESQL_DB_PASSWORD=""
OPENSHIFT_POSTGRESQL_DB_URL="postgresql://x:x@localhost/apihoyodecrimen"
REDIS_PASSWORD=""
OPENSHIFT_REDIS_HOST='127.0.0.1'
OPENSHIFT_REDIS_PORT='6379'
```

Create database with crime data csv file

```
psql -d apihoyodecrimen -U $OPENSHIFT_POSTGRESQL_DB_USERNAME -W
CREATE TABLE cuadrantes (
	cuadrante varchar (20),
	crime varchar (60),
	date  varchar (10),
	count int,
       year int,
       sector varchar(60),
       population integer,
       PRIMARY KEY(cuadrante, sector, crime, date)
);
COPY cuadrantes FROM '/tmp/cuadrantes.csv' DELIMITER ',' NULL AS 'NA' CSV HEADER;

CREATE TABLE municipios (cuadrante varchar (15),
sector varchar (60),
cvegeo  varchar (5),
municipio varchar(200),
    PRIMARY KEY(cuadrante)
);
COPY municipios FROM '/tmp/municipios.csv' DELIMITER ',' NULL AS 'NA' CSV HEADER;

CREATE TABLE crime_latlong (
        cuadrante varchar (20),
	crime varchar (60),
	date  varchar (10),
	hour  varchar (10),
	year  varchar (10),
	month  varchar (10),
        latitude double precision,
        longitude double precision,
        id integer,
        geom geometry,
        PRIMARY KEY(id)
);
COPY crime_latlong(cuadrante,crime,date,hour,year,month,latitude,longitude,id) FROM '/tmp/crime-lat-long.csv' DELIMITER ',' NULL AS 'NA' CSV HEADER;
UPDATE crime_latlong SET geom = ST_GeomFromText('POINT(' || longitude || ' ' || latitude || ')',4326);
CREATE INDEX crime_latlongi
  ON crime_latlong
  USING gist
  (geom );
CREATE INDEX cuadrantes_polygeom
  ON cuadrantes_poly
  USING gist
  (geom );
```

Create database from shapefile

```
shp2pgsql -s 4326 -W "latin1" -I -D cuadrantes-sspdf-no-errors.shp cuadrantes_poly > cuadrantes_poly.sql
ogr2ogr -f "GeoJSON" cuadrantes.geojson cuadrantes-sspdf-no-errors.shp
scp *.sql 543fe7165973cae5d30000c1@apihoyodecrimen-valle.rhcloud.com:app-root/data/
```

Upload sql file to postgresql database

```
psql apihoyodecrimen -c "CREATE EXTENSION postgis;"
psql -d apihoyodecrimen $OPENSHIFT_POSTGRESQL_DB_USERNAME  < cuadrantes_poly.sql
```
To create the Spanish translation

```
pybabel extract -F babel.cfg -o messages.pot .
pybabel update -i messages.pot -d translations
pybabel compile -d translations
```
