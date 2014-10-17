from datetime import datetime
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, and_
#from flask_cache import Cache
from redis import Redis
 
app = Flask(__name__)

#cache = Cache(app, config={
#            'CACHE_TYPE': 'redis',
#            'CACHE_REDIS_URL': 'redis://127.0.0.1:6379',
#        })

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

#@cache.cached(timeout=None, key_prefix='sectors')
@app.route('/v1/df/'
          '<string:crime>/'
          'all',
          methods=['GET'])
def sectors(crime, sector):
    if request.method == 'GET':
        results = Cuadrantes.query. \
            filter(
                   Cuadrantes.crime == crime). \
            with_entities(Cuadrantes.cuadrante,
                          Cuadrantes.sector,
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
                 'cuadrante': result.cuadrante,
                 'sector': result.sector,
                 'date': result.date,
                 'population': result.population / 12}
            json_results.append(d)
    return jsonify(items = json_results)

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

@app.route('/v1/list/crimes')
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

@app.route('/v1/list/cuadrantes')
def listcuadrantes():
    results = Cuadrantes.query. \
              with_entities(Cuadrantes.sector, Cuadrantes.cuadrante).\
              distinct().\
              all()
    json_results = []
    for result in results:
            d = {'sector': result.sector, 'cuadrante': result.cuadrante}
            json_results.append(d)
    return jsonify(items = json_results)

@app.route('/v1/list/sectores')
def listsectores():
    results = Cuadrantes.query. \
              with_entities(Cuadrantes.sector).\
              distinct().\
              all()
    json_results = []
    for result in results:
            d = {'sector': result.sector}
            json_results.append(d)
    return jsonify(items = json_results)



@app.route('/v1/top5/cuadrantes')
def top5cuadrantes():
    results = db.session.execute("""with crimes as
(select sum(count) as count,sector,cuadrante,max(population)as population, crime from cuadrantes where date >= '2013-08-01' and date <= '2014-07-01' group by cuadrante, sector, crime)
SELECT * from (SELECT count,crime,sector,cuadrante,rank() over (partition by crime order by count desc) as rank,population from crimes group by count,crime,sector,cuadrante,population) as temp2 where rank <= 5 order by crime, count, cuadrante, sector desc""")
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

@app.route('/v1/top5/sectores')
def top5sectores():
    results = db.session.execute("""with crimes as
(select (sum(count) / (sum(population::float) /12 )* 100000) as rate,sum(count) as count,sector,sum(population)/12 as population, crime from cuadrantes  where date >= '2013-08-01' and date <= '2014-07-01' group by sector, crime)
SELECT * from (SELECT count,rate,crime,sector,rank() over (partition by crime order by rate desc) as rank,population from crimes group by count,crime,sector,population, rate) as temp2 where rank <= 5""")
    json_results = []
    for result in results:
            d = {'count': result.count,
                 'crime': result.crime,
                 'sector': result.sector,
                 'rate': result.rate,
                 'rank': result.rank,
                 'population': result.population}
            json_results.append(d)
    return jsonify(items = json_results)

@app.route('/v1/top5/changecuadrantes')
def top5changecuadrantes():
    results = db.session.execute("""with difference as
(select crime, cuadrante, sector, max(population) as population, sum(case when date = '2014-07-01' or date = '2014-06-01' or date='2014-05-01' THEN count ELSE 0 END) as y2014, sum(case when date = '2013-07-01' or date = '2013-06-01' or date='2013-05-01' THEN count ELSE 0 END) as y2013, sum(case when date = '2014-07-01' or date = '2014-06-01' or date='2014-05-01' THEN count ELSE 0 END) - sum(case when date = '2013-07-01' or date = '2013-06-01' or date='2013-05-01' THEN count ELSE 0 END) as diff  from cuadrantes group by cuadrante, sector, crime order by diff desc)
SELECT * from (SELECT rank() over (partition by crime order by diff desc) as rank,crime,cuadrante,sector,population, y2013, y2014,diff from difference group by diff,crime,sector,cuadrante, population, y2013, y2014) as temp where rank <= 5  order by crime, rank, cuadrante, sector asc""")
    json_results = []
    for result in results:
            d = {
                 'crime': result.crime,
                 'sector': result.sector,
                 'cuadrante': result.cuadrante,
                 'rank': result.rank,
                 'population': result.population,
                 'start_period': result.y2013,
                 'end_period': result.y2014,
                 'difference': result.diff}
            json_results.append(d)
    return jsonify(items = json_results)


 
if __name__ == '__main__':
    app.run()

from api import *
db.create_all()
