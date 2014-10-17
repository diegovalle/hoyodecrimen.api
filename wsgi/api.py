from datetime import datetime
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, and_
from flask_cache import Cache
#from redis import Redis
 

START_STATE = '2013-01'
#LAST_STRING = 'last'


app = Flask(__name__)

cache = Cache(app, config={
            'CACHE_TYPE': 'redis',
            'CACHE_REDIS_URL': 'redis://127.0.0.1:16379',
        })

app.config.from_pyfile('apihoyodecrimen.cfg')
db = SQLAlchemy(app)

#from api import *
db.create_all()

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

def jsonp(f):
    """Wraps JSONified output for JSONP"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        callback = request.args.get('callback', False)
        if callback:
            content = str(callback) + '(' + str(f(*args, **kwargs).data) + ')'
            return current_app.response_class(content, mimetype='application/javascript')
        else:
            return f(*args, **kwargs)

    return decorated_function

def results_to_json(results):
    json_results = []
    if len(results) > 0:
        keys = results[0].keys()
        for result in results:
            d = {}
            for i, key in enumerate(keys):
                if key == "date":
                    d["year"] = int(result[i][0:4])
                    d["month"] = int(result[i][5:7])
                else:
                    d[key] = result[i]
            json_results.append(d)

        return jsonify(rows=json_results) #Response(json.dumps(json_results),  mimetype='application/json')#
    else:
        return jsonify(rows=[])

def monthsub(date, months):
    m = (int(date[5:7]) + months) % 12
    y = int(date[0:4]) + ((int(date[5:7])) + months - 1) // 12
    if not m: 
        m = 12
    return str(y) + '-' + str(m).zfill(2) + '-01'

def check_date_month(str):
    try:
        time.strptime(str, '%Y-%m')
        valid = True
    except ValueError:
        valid = False
    return valid
 
@app.route('/')
def index():
    return "Hello from API"

@app.route('/v1/df/'
          'all',
          methods=['GET'])
def df_all_crime():
    if request.method == 'GET':
        results = Cuadrantes.query. \
            with_entities(func.lower(Cuadrantes.crime),
                          Cuadrantes.date,
                          func.sum(Cuadrantes.count).label('count'),
                          func.sum(Cuadrantes.population).label('population')). \
            group_by(Cuadrantes.crime, Cuadrantes.date). \
            order_by(Cuadrantes.crime, Cuadrantes.date). \
            all()
    return results_to_json(results)


@cache.cached(timeout=None)
@app.route('/v1/df/'
          '<string:crime>',
          methods=['GET'])
def df_all(crime):
    if request.method == 'GET':
        results = Cuadrantes.query. \
            filter(Cuadrantes.crime == crime). \
            with_entities(func.lower(Cuadrantes.crime),
                          Cuadrantes.date,
                          func.sum(Cuadrantes.count).label('count'),
                          func.sum(Cuadrantes.population).label('population')). \
            group_by(Cuadrantes.date, Cuadrantes.crime). \
            order_by(Cuadrantes.date). \
            all()
    return results_to_json(results)

@app.route('/v1/cuadrantes/'
          '<string:crime>/'
          '<string:cuadrante>',
          methods=['GET'])
def cuadrantes(crime, cuadrante):
    if request.method == 'GET':
        results = Cuadrantes.query. \
            filter(Cuadrantes.cuadrante == cuadrante,
                   Cuadrantes.crime == crime). \
            with_entities(func.lower(Cuadrantes.cuadrante),
                          func.lower(Cuadrantes.sector),
                          func.lower(Cuadrantes.crime),
                          Cuadrantes.date,
                          Cuadrantes.count,
                          Cuadrantes.population) \
            .order_by(Cuadrantes.date) \
            .all()
        #results = db.session.execute("select cuadrante, sector, crime, date, count, population from cuadrantes order by crime, date, cuadrante, sector where cuadrante = ?", (cuadrante_id,))
    return results_to_json(results)

@app.route('/v1/sectores/'
          '<string:crime>/'
          '<string:sector>',
          methods=['GET'])
def sectors(crime, sector):
    if request.method == 'GET':
        results = Cuadrantes.query. \
            filter(Cuadrantes.sector == sector,
                   Cuadrantes.crime == crime). \
            with_entities(func.lower(Cuadrantes.sector),
                          func.lower(Cuadrantes.crime),
                          Cuadrantes.date,
                          func.sum(Cuadrantes.count).label('count'),
                          func.sum(Cuadrantes.population).label('population')). \
            group_by(Cuadrantes.crime, Cuadrantes.date, Cuadrantes.sector). \
            order_by(Cuadrantes.date). \
            all()
    return results_to_json(results)

@app.route('/v1/list/crimes')
def listcrimes():
    results = Cuadrantes.query. \
              with_entities(func.lower(Cuadrantes.crime)).\
              distinct().\
              all()
    json_results = []
    for result in results:
            d = {'crime': result.crime}
            json_results.append(d)
    return jsonify(rows = json_results)

@app.route('/v1/list/cuadrantes')
def listcuadrantes():
    results = Cuadrantes.query. \
              with_entities(func.lower(Cuadrantes.sector), func.lower(Cuadrantes.cuadrante)).\
              distinct().\
              all()
    return results_to_json(results)

@app.route('/v1/list/sectores')
def listsectores():
    results = Cuadrantes.query. \
              with_entities(func.lower(Cuadrantes.sector)).\
              distinct().\
              all()
    return results_to_json(results)



@app.route('/v1/top5/cuadrantecount')
def top5cuadrantes():
    max_date = Cuadrantes.query. \
            filter(). \
            with_entities(func.max(Cuadrantes.date).label('date')). \
            scalar()
    start_date = monthsub(max_date, -11)
    sql_query = """with crimes as
(select sum(count) as count,sector,cuadrante,max(population)as population, crime from cuadrantes where date >= '{0}' and date <= '{1}' group by cuadrante, sector, crime)
SELECT * from (SELECT count,crime,sector,cuadrante,rank() over (partition by crime order by count desc) as rank,population from crimes group by count,crime,sector,cuadrante,population) as temp2 where rank <= 5 order by crime, count, cuadrante, sector desc""".format(start_date, max_date)
    results = db.session.execute(sql_query)
    return results_to_json(dict(zip(results.keys(), results)))

@app.route('/v1/top5/sectorrate')
def top5sectores():
    max_date = Cuadrantes.query. \
            filter(). \
            with_entities(func.max(Cuadrantes.date).label('date')). \
            scalar()
    start_date = monthsub(max_date, -11)
    sql_query = """with crimes as
(select (sum(count) / (sum(population::float) /12 )* 100000) as rate,sum(count) as count,sector,sum(population)/12 as population, crime from cuadrantes  where date >= '{0}' and date <= '{1}' group by sector, crime)
SELECT * from (SELECT count,rate,crime,sector,rank() over (partition by crime order by rate desc) as rank,population from crimes group by count,crime,sector,population, rate) as temp2 where rank <= 5""".format(start_date, max_date)
    results = db.session.execute(sql_query)
    return results_to_json(dict(zip(results.keys(), results)))

@app.route('/v1/top5/changecuadrantes')
def top5changecuadrantes():
    start=request.args.get('start', START_STATE)
    end=request.args.get('end', LAST_STRING)
    if end != 'last':
        if not check_date_month(end):
            abort(abort(make_response('something is wrong with the end date you provided', 400)))
    if not check_date_month(start):
        abort(abort(make_response('something is wrong with the start date you provided', 400)))
    max_date = Cuadrantes.query. \
            filter(). \
            with_entities(func.max(Cuadrantes.date).label('date')). \
            scalar()
    max_date_minus3 = monthsub(max_date, -2)
    max_date_last_year = monthsub(max_date, -12)
    max_date_last_year_minus3 = monthsub(max_date, -14) 
    results = db.session.execute("""with difference as
(select crime, cuadrante, sector, max(population) as population, sum(case when date = '2014-07-01' or date = '2014-06-01' or date='2014-05-01' THEN count ELSE 0 END) 
as end_period, sum(case when date = '2013-07-01' or date = '2013-06-01' or date='2013-05-01' THEN count ELSE 0 END) as start_period, sum(case when date = '2014-07-01' or date = '2014-06-01' or date='2014-05-01' THEN count ELSE 0 END) - sum(case when date = '2013-07-01' or date = '2013-06-01' or date='2013-05-01' THEN count ELSE 0 END) as diff  from cuadrantes group by cuadrante, sector, crime order by diff desc)
SELECT * from (SELECT rank() over (partition by crime order by diff desc) as rank,crime,cuadrante,sector,population, start_period, end_period,diff from difference group by diff,crime,sector,cuadrante, population, start_period, end_period) as temp where rank <= 5  order by crime, rank, cuadrante, sector asc""")
    return results_to_json(dict(zip(results.keys(), results)))


 
if __name__ == '__main__':
    app.config['PROFILE'] = True
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[30])
    app.run()

