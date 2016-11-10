--CREATE EXTENSION IF NOT EXISTS postgis;
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
TRUNCATE TABLE cuadrantes;
--COPY cuadrantes FROM '/tmp/cuadrantes.csv' DELIMITER ',' NULL AS 'NA' CSV HEADER;

CREATE TABLE pgj (
	crime varchar (60),
	date  varchar (10),
	count int,
       PRIMARY KEY(crime, date)
);
TRUNCATE TABLE pgj;
--COPY pgj FROM '/tmp/pgj.csv' DELIMITER ',' NULL AS 'NA' CSV HEADER;

CREATE TABLE municipios (
cuadrante varchar (15),
sector varchar (60),
cvegeo  varchar (5),
municipio varchar(200),
    PRIMARY KEY(cuadrante)
);
TRUNCATE TABLE municipios;
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
TRUNCATE TABLE crime_latlong;
--COPY crime_latlong(cuadrante,crime,date,hour,year,month,latitude,longitude,id) FROM '/tmp/crime-lat-long.csv' DELIMITER ',' NULL AS 'NA' CSV HEADER;
