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
OPENSHIFT_APP_UUID=true (when running in production)
```

Create database with crime data csv file

```sh
#sudo -u postgres psql postgres
#CREATE DATABASE apihoyodecrimen OWNER deploy; 
#GRANT ALL PRIVILEGES ON DATABASE apihoyodecrimen TO deploy;
#scp cuadrantes.csv 543fe7165973cae5d30000c1@apihoyodecrimen-valle.rhcloud.com:/tmp 
psql -d apihoyodecrimen -U $OPENSHIFT_POSTGRESQL_DB_USERNAME -W
```

```sql
CREATE EXTENSION postgis;
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
--COPY cuadrantes FROM '/tmp/cuadrantes.csv' DELIMITER ',' NULL AS 'NA' CSV HEADER;

CREATE TABLE pgj (
	crime varchar (60),
	date  varchar (10),
	count int,
       PRIMARY KEY(crime, date)
);
--COPY pgj FROM '/tmp/pgj.csv' DELIMITER ',' NULL AS 'NA' CSV HEADER;

CREATE TABLE municipios (cuadrante varchar (15),
sector varchar (60),
cvegeo  varchar (5),
municipio varchar(200),
    PRIMARY KEY(cuadrante)
);
--COPY municipios FROM '/tmp/municipios.csv' DELIMITER ',' NULL AS 'NA' CSV HEADER;

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
--COPY crime_latlong(cuadrante,crime,date,hour,year,month,latitude,longitude,id) FROM '/tmp/crime-lat-long.csv' DELIMITER ',' NULL AS 'NA' CSV HEADER;
```

```sh
psql -d apihoyodecrimen -U $OPENSHIFT_POSTGRESQL_DB_USERNAME -W -c "\copy cuadrantes (cuadrante,crime,date,count,year,sector,population) from '/tmp/cuadrantes.csv' with delimiter as ','  NULL AS 'NA' CSV HEADER"
psql -d apihoyodecrimen -U $OPENSHIFT_POSTGRESQL_DB_USERNAME -W -c "\copy municipios (cuadrante,sector,cvegeo,municipio) from '/tmp/municipios.csv' with delimiter as ','  NULL AS 'NA' CSV HEADER"
psql -d apihoyodecrimen -U $OPENSHIFT_POSTGRESQL_DB_USERNAME -W -c "\copy pgj (crime,date,count) from '/tmp/pgj.csv' with delimiter as ','  NULL AS 'NA' CSV HEADER"
psql -d apihoyodecrimen -U $OPENSHIFT_POSTGRESQL_DB_USERNAME -W -c "\copy crime_latlong  (cuadrante,crime,date,hour,year,month,latitude,longitude,id) from '/tmp/crime-lat-long.csv' with delimiter as ','  NULL AS 'NA' CSV HEADER"
```

```sql
UPDATE crime_latlong SET geom = ST_GeomFromText('POINT(' || longitude || ' ' || latitude || ')',4326);
--CREATE INDEX crime_latlongi_geography ON crime_latlong USING gist( (geom::geography) );
CREATE INDEX crime_latlongi_castgeography ON crime_latlong USING gist( CAST(geom AS geography(GEOMETRY,-1) ));
CREATE INDEX crime_latlongi
  ON crime_latlong
  USING gist
  (geom );
CREATE INDEX crime_crime
  ON crime_latlong
  (crime);
CREATE INDEX pgj_crime
  ON pgj
  (crime);
CREATE INDEX crime_crime_date2
  ON crime_latlong
  (crime, date);
CREATE INDEX cuadrantes_polygeom
  ON cuadrantes_poly
  USING gist
  (geom );
CREATE INDEX cuadrantes_polygeom_cuadrante
  ON cuadrantes_poly
  (id,sector);
CREATE INDEX cuadrantes_cuadrante_crime_date
  ON cuadrantes
  (cuadrante, crime, date);
CREATE INDEX cuadrantes_date_null_desc
ON cuadrantes (date DESC NULLS LAST);
CREATE INDEX cuadrantes_cuadrante
ON cuadrantes (cuadrante);
CREATE INDEX cuadrantes_crime_null
  ON cuadrantes
  (crime ASC NULLS LAST);

CREATE INDEX cuadrantes_crime_partial
  ON cuadrantes
  ( crime)
WHERE (upper(cuadrantes.crime) = 'HOMICIDIO DOLOSO' OR upper(cuadrantes.crime) = 'LESIONES POR ARMA DE FUEGO' OR upper(cuadrantes.crime) = 'ROBO DE VEHICULO AUTOMOTOR S.V.' OR upper(cuadrantes.crime) = 'ROBO DE VEHICULO AUTOMOTOR C.V.' OR upper(cuadrantes.crime) = 'ROBO A TRANSEUNTE C.V.');
--psql -d scalehoyodecrimen -U $OPENSHIFT_POSTGRESQL_DB_USERNAME -W -f create_db.sql
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
