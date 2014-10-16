from datetime import datetime
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, and_
 
app = Flask(__name__)
 
app.config.from_pyfile('apihoyodecrimen.cfg')
db = SQLAlchemy(app)

#psql -d dbname -U username -W
#CREATE TABLE cuadrantes (
#	cuadrante varchar (10),
#	crime varchar (60),
#	date  varchar (10),
#	count int,
#        year int,
#        sector varchar(60),
#        population integer,
#        PRIMARY KEY(cuadrante, sector, crime, date)
#);
#COPY cuadrantes FROM '/var/lib/openshift/543fe7165973cae5d30000c1/app-root/repo/data/cuadrantes.csv' DELIMITER ',' NULL AS 'NA' CSV HEADER;

class Cuadrantes(db.Model):
    __tablename__ = 'cuadrantes'
    cuadrante = db.Column(db.String(7), primary_key=True)
    crime = db.Column(db.String(60))
    date = db.Column(db.String(10))
    count = db.Column(db.Integer)
    year = db.Column(db.Integer)
    sector = db.Column(db.String(60))
    population = db.Column(db.Integer)

    def __init__(self, cuadrante, crime, date, count, year, sector, population):
        self.cuadrante = title
        self.crime = text
        self.date = date
        self.count = count
        self.year = year
        self.sector = sector
        self.population = population
 
@app.route('/')
def index():
    return "Hello from API"

@app.route('/v1/cuadrantes/'
          '<string:crime>/'
          '<string:cuadrante>',
          methods=['GET'])
def cuadrantes(crime, cuadrante):
    if request.method == 'GET':
        results = Cuadrantes.query. \
            filter(Cuadrantes.cuadrante == cuadrante,
                   Cuadrantes.crime == crime). \
            with_entities(Cuadrantes.cuadrante,
                          Cuadrantes.sector,
                          Cuadrantes.crime,
                          Cuadrantes.date,
                          Cuadrantes.count,
                          Cuadrantes.population) \
            .order_by(Cuadrantes.date) \
            .all()
        #results = db.session.execute("select cuadrante, sector, crime, date, count, population from cuadrantes order by crime, date, cuadrante, sector where cuadrante = ?", (cuadrante_id,))
    json_results = []
    for result in results:
            d = {'count': result.count,
                 'crime': result.crime,
                 'sector': result.sector,
                 'cuadrante': result.cuadrante,
                 'date': result.date,
                 'population': result.population}
            json_results.append(d)
    return jsonify(items = json_results)

@app.route('/v1/sectores/'
          '<string:crime>/'
          '<string:sector>',
          methods=['GET'])
def sectors(crime, sector):
    if request.method == 'GET':
        results = Cuadrantes.query. \
            filter(Cuadrantes.sector == sector,
                   Cuadrantes.crime == crime). \
            with_entities(Cuadrantes.sector,
                          Cuadrantes.crime,
                          Cuadrantes.date,
                          func.sum(Cuadrantes.count).label('count'),
                          func.sum(Cuadrantes.population).label('population')). \
            group_by(Cuadrantes.crime, Cuadrantes.date, Cuadrantes.sector). \
            order_by(Cuadrantes.date). \
            all()
    json_results = []
    for result in results:
            d = {'count': result.count,
                 'crime': result.crime,
                 'sector': result.sector,
                 'date': result.date,
                 'population': result.population / 12}
            json_results.append(d)
    return jsonify(items = json_results)

@app.route('/v1/list/crimes/')
def listcrimes():
    results = Cuadrantes.query. \
              with_entities(Cuadrantes.crime).\
              distinct().\
              all()
   json_results = []
   for result in results:
            d = {'crime': result.crime}
            json_results.append(d)
    return jsonify(items = json_results)



@app.route('/v1/top5/cuadrantes')
def top5cuadrantes():
    results = db.session.execute("""with crimes as
(select sum(count) as count,sector,cuadrante,max(population)as population, crime from cuadrantes where date >= '2013-08-01' and date <= '2014-07-01' group by cuadrante, sector, crime)
SELECT * from (SELECT count,crime,sector,cuadrante,rank() over (partition by crime order by count desc) as rank,population from crimes group by count,crime,sector,cuadrante,population) as temp2 where rank <= (SELECT rank from (SELECT count,cuadrante,rank() over (partition by crime order by count desc) as rank, row_number() OVER (ORDER BY count desc) AS rownum from crimes) as rank10 where rownum = 10) order by crime, rank,sector, cuadrante""")
    json_results = []
    for result in results:
            d = {'count': result.count,
                 'crime': result.crime,
                 'sector': result.sector,
                 'cuadrante': result.cuadrante,
                 'rank': result.rank,
                 'population': result.population}
            json_results.append(d)
    return jsonify(items = json_results)
 
if __name__ == '__main__':
    app.run()

from api import *
db.create_all()
