from datetime import datetime
from flask import Blueprint, Flask, jsonify, request, abort, \
    make_response, url_for, send_from_directory,\
    send_file, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text, literal_column, literal
from sqlalchemy import func, and_
from flask.ext.cache import Cache
from flask.ext.assets import Environment, Bundle
from werkzeug.contrib.profiler import ProfilerMiddleware
from functools import wraps
from geoalchemy2.elements import WKTElement
import time
import os
from api.models import db, Cuadrantes, Cuadrantes_Poly
#from redis import Redis
from api.api import API, cache
from flask.ext.compress import Compress
from flask.ext.babel import Babel

_basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.register_blueprint(API)
db = SQLAlchemy(app)
app.config.from_pyfile('apihoyodecrimen.cfg')

cache.init_app(app)
assets = Environment(app)
assets.versions = 'timestamp'    # use the last modified timestamp
babel = Babel(app)


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


js_pip_req = Bundle("js/jquery.min.js", "js/jquery.dropotron.min.js", "js/skel.min.js",
            "js/skel-layers.min.js",
            "js/init.js", "js/underscore-min.js", "js/leaflet.js",
            "js/leaflet-pip.js",
            "js/topojson.v1.min.js", "js/d3.v3.min.js", "js/c3.min.js",
            "js/jquery.1.8.3.min.js", "js/modernizr.js",
            filters='jsmin', output='js/packed-pip-req.js')
assets.register('js_pip_req', js_pip_req)

js_pip = Bundle("js/pip.js", filters ="jsmin", output="js/js_pip.js")
assets.register("js_pip", js_pip)


@app.route('/')
def index_html():
    return "If it's in a word, or if it's in a book you can't get rid of the Babadook"


@app.route('/en/')
def api_home_html():
    return render_template('pip.html')


@app.route('/api/')
def api_index_html():
    return send_from_directory(os.path.join(_basedir, 'static', 'sphinx', 'html'), 'index.html')


@app.route('/api/<path:filename>')
def api_html(filename):
    if filename.endswith('/'):
         filename += 'index.html'
    return send_from_directory(os.path.join(_basedir, 'static', 'sphinx', 'html'), filename)


@app.route('/en/rates')
def index():
    return render_template('rates-sectores.html')


@app.route('/en/trends')
def change():
    return render_template('change-cuadrantes.html')


@app.route('/en/counts')
def counts():
    return render_template('counts-cuadrantes.html')


@app.route('/en/sectores-map')
def sectores_map():
    return render_template('sectores-map.html')


@app.route('/en/cuadrantes-map')
def cuadrantes_map():
    return render_template('cuadrantes-map.html')


# Google webmaster verification
@app.route('/google055ef027e7764e4d.html')
def google055ef027e7764e4d():
    return 'google-site-verification: google055ef027e7764e4d.html'


@app.route('/api/_static/<path:filename>')
def static__api(filename):
    return send_from_directory(os.path.join(_basedir, 'static',
                                            'sphinx', 'html', '_static'),
                               filename)


@app.route('/css/<path:filename>')
def static_css(filename):
    return send_from_directory(os.path.join(_basedir, 'static','css'), filename)


@app.route('/font/<path:filename>')
def static_font(filename):
    return send_from_directory(os.path.join(_basedir, 'static','font'), filename)

@app.route('/fonts/<path:filename>')
def static_fonts(filename):
    return send_from_directory(os.path.join(_basedir, 'static','fonts'), filename)


@app.route('/js/<path:filename>')
def static_js(filename):
    return send_from_directory(os.path.join(_basedir, 'static','js'), filename)


@app.route('/images/<path:filename>')
def static_images(filename):
    return send_from_directory(os.path.join(_basedir, 'static','images'),
                               filename)

@app.route('/favicon.ico')
def static_images_favicon():
    return send_from_directory(os.path.join(_basedir, 'static','images'),
                               'favicon.ico')

@app.route('/apple-touch-icon-57x57.png')
def static_images_57():
    return send_from_directory(os.path.join(_basedir, 'static','images'),
                               'apple-touch-icon-57x57.png')


@app.route('/apple-touch-icon.png')
def static_images_apple():
    return send_from_directory(os.path.join(_basedir, 'static','images'),
                               'apple-touch-icon.png')

@app.route('/apple-touch-icon-72x72.png')
def static_images_72():
    return send_from_directory(os.path.join(_basedir, 'static','images'),
                               'apple-touch-icon-72x72.png')


@app.route('/apple-touch-icon-76x76.png')
def static_images_76():
    return send_from_directory(os.path.join(_basedir, 'static','images'),
                               'apple-touch-icon-76x76.png')


@app.route('/apple-touch-icon-114x114.png')
def static_images_114():
    return send_from_directory(os.path.join(_basedir, 'static','images'),
                               'apple-touch-icon-114x114.png')


@app.route('/apple-touch-icon-120x120.png')
def static_images_120():
    return send_from_directory(os.path.join(_basedir, 'static','images'),
                               'apple-touch-icon-120x120.png')


@app.route('/apple-touch-icon-144x144.png')
def static_images_144():
    return send_from_directory(os.path.join(_basedir, 'static','images'),
                               'apple-touch-icon-144x144.png')


@app.route('/apple-touch-icon-152x152.png')
def static_images_152():
    return send_from_directory(os.path.join(_basedir, 'static','images'),
                               'apple-touch-icon-152x152.png')



if __name__ == '__main__':
    with app.app_context():
        cache.clear()

    db.create_all()

    debug = False
    # Running locally
    if 'OPENSHIFT_APP_UUID' not in os.environ:
        app.config['PROFILE'] = True
        app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[30])
        debug = True
    else:
        Compress(app)
    app.run(debug=debug)
