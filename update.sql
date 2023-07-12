-- psql -d apihoyodecrimen -f update.sql
\set cuadrantes :temp '/cuadrantes-pgj.csv'
\set pgj :temp '/pgj.csv'
\set crimelatlongpgj :temp '/crime-lat-long-pgj.csv'

BEGIN;
-- LOCK TABLE 'table' IN SHARE ROW EXCLUSIVE mode;
-- cuadrantes
--DROP TABLE IF EXISTS cuadrantes_new;
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
\set command1 '\\copy cuadrantes_new (cuadrante,crime,date,count,year,sector,population) from ' :'cuadrantes' ' with delimiter as '','' NULL AS ''NA'' CSV HEADER; '
:command1
-- create indexes
CREATE INDEX ON cuadrantes_new (crime ASC NULLS LAST);
CREATE INDEX ON cuadrantes_new (cuadrante);
CREATE INDEX ON cuadrantes_new (date DESC NULLS LAST);
CREATE INDEX ON cuadrantes_new (cuadrante, crime, date);
CREATE INDEX ON cuadrantes_new ((upper(crime)), date, sector);
CREATE INDEX ON cuadrantes_new ((upper(crime)), date, cuadrante);
CREATE INDEX ON cuadrantes_new USING btree ((upper(cuadrante)), crime);
-- pgj
--DROP TABLE IF EXISTS pgj_new;
CREATE TABLE pgj_new (
  crime varchar (60),
  date varchar (10),
  count int,
  PRIMARY KEY(crime, date)
);
\set command2 '\\copy pgj_new (crime, date, count) from ' :'pgj' ' with delimiter as '','' NULL AS ''NA'' CSV HEADER;'
:command2
CREATE INDEX ON pgj_new (crime);
-- crime_latlong
TRUNCATE TABLE crime_latlong;
\set command3 '\\copy crime_latlong (cuadrante,crime,date,hour,year,month,latitude,longitude,id) from ' :'crimelatlongpgj' ' with delimiter as '','' NULL AS ''NA'' CSV HEADER;'
:command3
UPDATE crime_latlong
SET geom = ST_GeomFromText(
    'POINT(' || longitude || ' ' || latitude || ')',
    4326
  );
-- The ALTER TABLE ... RENAME TO command takes an Access Exclusive lock on 'table'
ALTER TABLE cuadrantes
  RENAME TO cuadrantes_old;
ALTER TABLE cuadrantes_new
  RENAME TO cuadrantes;
DROP TABLE cuadrantes_old;
ALTER TABLE pgj
  RENAME TO pgj_old;
ALTER TABLE pgj_new
  RENAME TO pgj;
DROP TABLE pgj_old;
COMMIT;
