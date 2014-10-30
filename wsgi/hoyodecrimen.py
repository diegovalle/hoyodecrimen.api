from datetime import datetime
from flask import Blueprint, Flask, jsonify, request, abort, make_response, url_for, send_from_directory,send_file, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text, literal_column, literal
from sqlalchemy import func, and_
from flask.ext.cache import Cache
from werkzeug.contrib.profiler import ProfilerMiddleware
from functools import wraps
from geoalchemy2.elements import WKTElement
import time
import os
from api.models import db, Cuadrantes, Cuadrantes_Poly
#from api.api import API
#from redis import Redis
from api.api import API, cache

_basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.register_blueprint(API)
db = SQLAlchemy(app)
app.config.from_pyfile('apihoyodecrimen.cfg')

cache.init_app(app)


def add_response_headers(headers={}):
    """This decorator adds the headers passed in to the response"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            resp = make_response(f(*args, **kwargs))
            h = resp.headers
            for header, value in headers.items():
                h[header] = value
            return resp
        return decorated_function
    return decorator


def noframes(f):
    """This decorator passes X-Robots-Tag: noindex"""
    @wraps(f)
    @add_response_headers({'X-Frame-Options': 'DENY'})
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated_function

# Simple HTTP error handling
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.route('/api/')
def api_html():
    return app.send_static_file(os.path.join('api', 'index.html'))

@app.route('/rates')
def index():
    return app.send_static_file(os.path.join('', 'rates-sectores.html'))

@app.route('/change')
def change():
    return app.send_static_file(os.path.join('', 'change-cuadrantes.html'))

@app.route('/counts')
def counts():
    return app.send_static_file(os.path.join('', 'counts-cuadrantes.html'))

@app.route('/sectores-map')
def sectores_map():
    return app.send_static_file(os.path.join('', 'sectores-map.html'))

@app.route('/cuadrantes-map')
def cuadrantes_map():
    return app.send_static_file(os.path.join('', 'cuadrantes-map.html'))

@app.route('/api/_static/<path:filename>')
def static__api(filename):
    return send_from_directory(os.path.join(_basedir, 'static/api/_static'), filename)

@app.route('/css/<path:filename>')
def static_css(filename):
    return send_from_directory(os.path.join(_basedir, 'static/css'), filename)

@app.route('/js/<path:filename>')
def static_js(filename):
    return send_from_directory(os.path.join(_basedir, 'static/js'), filename)

@app.route('/font/<path:filename>')
def static_font(filename):
    return send_from_directory(os.path.join(_basedir, 'static/font'), filename)

@app.route('/images/<path:filename>')
def static_images(filename):
    return send_from_directory(os.path.join(_basedir, 'static/images'), filename)



if __name__ == '__main__':
    with app.app_context():
        cache.clear()

    db.create_all()

    debug=False
    if 'OPENSHIFT_APP_UUID' not in os.environ:
        app.config['PROFILE'] = True
        app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[30])
        debug=True
    app.run(debug=debug)










