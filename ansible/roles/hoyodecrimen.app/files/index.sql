UPDATE crime_latlong SET geom = ST_GeomFromText('POINT(' || longitude || ' ' || latitude || ')',4326);
--CREATE INDEX crime_latlongi_geography ON crime_latlong USING gist( (geom::geography) );
CREATE INDEX crime_latlongi_castgeography ON crime_latlong USING gist( CAST(geom AS geography(GEOMETRY,-1) ));
CREATE INDEX crime_latlongi_castgeography_4326 ON crime_latlong USING gist( CAST(geom AS geography(GEOMETRY,4326) ));
CREATE INDEX crime_latlongi_castgeography_2163 ON crime_latlong USING GIST (ST_Transform(geom, 2163));
CREATE INDEX crime_latlong_crime_date_desc ON crime_latlong (crime DESC, date DESC);
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
CREATE INDEX cuadrantes_polygeom_2163
  ON cuadrantes_poly
  USING gist
  (ST_Transform(geom, 2163));
CREATE INDEX cuadrantes_polygeom_cuadrante
  ON cuadrantes_poly
  (id,sector);
CREATE INDEX cuadrantes_cuadrante_crime_date
  ON cuadrantes
  (cuadrante, crime, date);
CREATE INDEX cuadrantes_upper_crime_date_sector
  ON cuadrantes
  ( (upper(cuadrantes.crime)), date, sector);
CREATE INDEX cuadrantes_date_null_desc
ON cuadrantes (date DESC NULLS LAST);
CREATE INDEX cuadrantes_cuadrante
ON cuadrantes (cuadrante);
CREATE INDEX cuadrantes_crime_null
  ON cuadrantes
  (crime ASC NULLS LAST);
CREATE INDEX uppper_cuadrantes_crime ON cuadrantes USING btree ((upper(cuadrante)), crime);
CREATE INDEX cuadrantes_crime_partial
  ON cuadrantes
  ( crime)
WHERE (upper(cuadrantes.crime) = 'HOMICIDIO DOLOSO' OR upper(cuadrantes.crime) = 'LESIONES POR ARMA DE FUEGO' OR upper(cuadrantes.crime) = 'ROBO DE VEHICULO AUTOMOTOR S.V.' OR upper(cuadrantes.crime) = 'ROBO DE VEHICULO AUTOMOTOR C.V.' OR upper(cuadrantes.crime) = 'ROBO A TRANSEUNTE C.V.');

--AI

CREATE INDEX crime_latlong_idx_geom ON "crime_latlong" USING GIST ("geom");

CREATE INDEX cuadrantes_idx_uppercri_uppersec_date ON "cuadrantes" ((upper(crime)),(upper(sector)),"date");
CREATE INDEX cuadrantes_idx_crime_date_sector ON "cuadrantes" ("crime","date","sector");

CREATE INDEX crime_latlong_idx_geom ON "crime_latlong" USING GIST ("geom");

CREATE INDEX cuadrantes_poly_idx_geom ON "cuadrantes_poly" USING GIST ("geom");

CREATE INDEX cuadrantes_idx_upper_upper_crime_date ON "cuadrantes" ((upper(crime)),(upper(cuadrante)),"crime","date");

CREATE INDEX crime_latlong_idx_geom ON "crime_latlong" USING GIST ("geom");

CREATE INDEX cuadrantes_idx_uppercri_uppercua_date ON "cuadrantes" ((upper(crime)),(upper(cuadrante)),"date");

--psql -d scalehoyodecrimen -U $OPENSHIFT_POSTGRESQL_DB_USERNAME -W -f create_db.sql
