from cgi import test
from flask import Flask, render_template, redirect, send_from_directory, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from src.code.Honeypots import ingest_honeypots
import os


app = Flask(__name__, template_folder=os.path.abspath('src/pages'))
limiter = Limiter(app, key_func = get_remote_address, default_limits=["20/minute", "200/hour"])
@app.errorhandler(429)
def ratelimit_handler(e):
    # TODO Log out user if logged in
    return render_template('rate-limit.html'), 429

honeypots = ingest_honeypots("data/honeypots.yaml")


# Static routes
@app.route('/', methods=["GET"])
@limiter.limit(None)
def root(): return redirect("dashboard", code=302)

@app.route('/login', methods=["GET"])
@limiter.limit(None)
def login(): return render_template('login.html')

@app.route('/dashboard', methods=["GET"])
@limiter.limit(None)
def dashboard(): return render_template('dashboard.html', count = len(honeypots), honeypots = honeypots)

@app.route('/profiler', methods=["GET"])
@limiter.limit(None)
def profiler(): return render_template('profiler.html')

@app.route('/stats', methods=["GET"])
@limiter.limit(None)
def stats(): return render_template('stats.html')

@app.route('/statistics', methods=["GET"])
@limiter.limit(None)
def statistics(): return redirect("stats", code=302)

@app.route('/about', methods=["GET"])
@limiter.limit(None)
def about(): return render_template('about-auth.html')


# Dynamic routes for assets
@app.route('/static/<path:path>')
@limiter.limit(None)
def send_report(path):
    return send_from_directory('static', path)


# API router (in development)
test_data = {
    '1Cbas2ZWQ8Kq': {
        'type': 'VPS',
        'os': 'Ubuntu 20.04',
        'owner': 12345,
        'updated': 1652262306,
        'health': 0
    },
    'w8w5t32JFMzT': {
        'type': 'VPS',
        'os': 'Ubuntu 20.04',
        'owner': 12345,
        'updated': 1651233737,
        'health': 1
    },
    'hFc8c7Hhr8wj': {
        'type': 'Database',
        'os': 'Ubuntu 20.04',
        'owner': 12345,
        'updated': 1651953237,
        'health': 3
    },
    '0ooQzs78Aizu': {
        'type': 'Database',
        'db-engine': 'mysql',
        'owner': 12345,
        'updated': 1651993737,
        'health': 0
    },
    '0ooQzs78Aizu': {
        'type': 'Database',
        'db-engine': 'mysql',
        'owner': 12345,
        'updated': 1651233737,
        'health': 0
    },
    '0SK8zO8VB8Wj': {
        'type': 'Database',
        'db-engine': 'mysql',
        'owner': 12345,
        'updated': 1651123437,
        'health': 0
    },
    'qVAUYY6C67tv': {
        'type': 'Database',
        'db-engine': 'mysql',
        'owner': 12345,
        'updated': 1651933123,
        'health': 2
    },
    'yCdPU4EtIk33': {
        'type': 'Database',
        'db-engine': 'mysql',
        'owner': 12345,
        'updated': 1651993737,
        'health': 0
    },
    'yCdPU4EtIk34': {
        'type': 'Database',
        'db-engine': 'mysql',
        'owner': 12345,
        'updated': 1651993737,
        'health': 0
    },
    'yCdPU4EtIk35': {
        'type': 'Database',
        'db-engine': 'mysql',
        'owner': 12345,
        'updated': 1651993737,
        'health': 0
    },
    'yCdPU4EtIk36': {
        'type': 'Database',
        'db-engine': 'mysql',
        'owner': 12345,
        'updated': 1652478564,
        'health': 0
    },
    'yCdPU4EtIk37': {
        'type': 'Database',
        'db-engine': 'mysql',
        'owner': 12345,
        'updated': 1651993737,
        'health': 0
    },
    'yCdPU4EtIk38': {
        'type': 'Database',
        'db-engine': 'mysql',
        'owner': 12345,
        'updated': 1652478558,
        'health': 0
    }
}

@app.route('/api/v1/honeypots', methods=["GET"])
@limiter.limit("120/minute;1200/hour", override_defaults=True)
def api_v1_honeypots(): return jsonify(test_data)


if __name__ == '__main__': app.run()