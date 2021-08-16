#!/bin/bash
set -euo pipefail #exit on error, undefined and prevent pipeline errors
IFS=$'\n\t'

SQL="
BEGIN;
-- LOCK TABLE 'table' IN SHARE ROW EXCLUSIVE mode;
-- cuadrantes
CREATE TABLE cuadrantes_new (
  cuadrante varchar (20),
  crime varchar (60),
  date varchar (10),
  count int,
  year int,
  sector varchar(60),
  population integer,
  PRIMARY KEY(cuadrante, sector, crime, date)
);
\ copy cuadrantes_new (
  cuadrante,
  crime,
  date,
  count,
  year,
  sector,
  population
)
from '/tmp/cuadrantes-pgj.csv' with delimiter as ',' NULL AS 'NA' CSV HEADER -- create indexes
  CREATE INDEX cuadrantes_crime_null ON cuadrantes_new (crime ASC NULLS LAST);
CREATE INDEX cuadrantes_cuadrante ON cuadrantes_new (cuadrante);
CREATE INDEX cuadrantes_date_null_desc ON cuadrantes_new (date DESC NULLS LAST);
CREATE INDEX cuadrantes_cuadrante_crime_date ON cuadrantes_new (cuadrante, crime, date);
CREATE INDEX cuadrantes_upper_crime_date_sector ON cuadrantes_new ((upper(cuadrantes.crime)), date, sector);
CREATE INDEX cuadrantes_upper_crime_date_cuadrante ON cuadrantes_new ((upper(cuadrantes.crime)), date, cuadrante);
CREATE INDEX uppper_cuadrantes_crime ON cuadrantes_new USING btree ((upper(cuadrante)), crime);
-- pgj
CREATE TABLE pgj_new (
  crime varchar (60),
  date varchar (10),
  count int,
  PRIMARY KEY(crime, date)
);
\ copy pgj_new (crime, date, count)
from '/tmp/pgj.csv' with delimiter as ',' NULL AS 'NA' CSV HEADER CREATE INDEX pgj_crime ON pgj_new (crime);
-- crime_latlong
TRUNCATE TABLE crime_latlong;
\ copy crime_latlong (
  cuadrante,
  crime,
  date,
  hour,
  year,
  month,
  latitude,
  longitude,
  id
)
from '/tmp/crime-lat-long-pgj.csv' with delimiter as ',' NULL AS 'NA' CSV HEADER
UPDATE crime_latlong
SET geom = ST_GeomFromText(
    'POINT(' || longitude || ' ' || latitude || ')',
    4326
  );
-- The ALTER TABLE ... RENAME TO command takes an Access Exclusive lock on 'table'
ALTER TABLE 'cuadrantes'
  RENAME TO 'cuadrantes_old';
ALTER TABLE 'cuadrantes_new'
  RENAME TO 'cuadrantes';
DROP TABLE 'cuadrantes_old';
ALTER TABLE 'pgj'
  RENAME TO 'pgj_old';
ALTER TABLE 'pgj_new'
  RENAME TO 'pgj';
DROP TABLE 'pgj_old';
COMMIT;
"

# scp -C crime-lat-long-pgj.csv cuadrantes-pgj.csv pgj.csv deploy@ip:/tmp
psql -d apihoyodecrimen -c "$SQL"
psql -d apihoyodecrimen -c "VACUUM ANALYZE crime_latlong;"
psql -d apihoyodecrimen -c "VACUUM ANALYZE cuadrantes;"
psql -d apihoyodecrimen -c "VACUUM ANALYZE pgj;"
