#!/bin/bash
set -euo pipefail #exit on error, undefined and prevent pipeline errors
IFS=$'\n\t'


CUADRANTES_TABLE="DROP TABLE  cuadrantes;
CREATE TABLE cuadrantes (
cuadrante varchar (20),
crime varchar (60),
date  varchar (10),
count int,
       year int,
       sector varchar(60),
       population integer,
       PRIMARY KEY(cuadrante, sector, crime, date)
);"
CUADRANTES_INDEX="CREATE INDEX cuadrantes_crime_null  ON cuadrantes
  (crime ASC NULLS LAST);
CREATE INDEX cuadrantes_cuadrante ON cuadrantes (cuadrante);
CREATE INDEX cuadrantes_date_null_desc ON cuadrantes (date DESC NULLS LAST);
CREATE INDEX cuadrantes_cuadrante_crime_date  ON cuadrantes
  (cuadrante, crime, date);
"

# scp -C crime-lat-long-pgj.csv cuadrantes-pgj.csv pgj.csv deploy@ip:/tmp
psql -d apihoyodecrimen -c "TRUNCATE TABLE  crime_latlong;"
psql -d apihoyodecrimen -c "$CUADRANTES_TABLE"
psql -d apihoyodecrimen -c "TRUNCATE TABLE pgj;"
psql -d apihoyodecrimen -c "\copy cuadrantes (cuadrante,crime,date,count,year,sector,population) from '/tmp/cuadrantes-pgj.csv' with delimiter as ','  NULL AS 'NA' CSV HEADER"
psql -d apihoyodecrimen  -c "\copy crime_latlong  (cuadrante,crime,date,hour,year,month,latitude,longitude,id) from '/tmp/crime-lat-long-pgj.csv' with delimiter as ','  NULL AS 'NA' CSV HEADER"
psql -d apihoyodecrimen -c "\copy pgj (crime,date,count) from '/tmp/pgj.csv' with delimiter as ','  NULL AS 'NA' CSV HEADER"
psql -d apihoyodecrimen -c "UPDATE crime_latlong SET geom = ST_GeomFromText('POINT(' || longitude || ' ' || latitude || ')',4326);"
psql -d apihoyodecrimen -c "$CUADRANTES_INDEX"
