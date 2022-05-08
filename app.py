from flask import Flask, render_template, redirect, send_from_directory
from src.code.Honeypots import VPS, ingest_honeypots
import os

app = Flask(__name__,
    template_folder=os.path.abspath('src/pages'))

"""honeypots = ["1Cbas2ZWQ8Kq", "4pU5QL94LhL5", "w8w5t32JFMzT",
    "PG4f8DE87v7U", "fBHpk7qhF10q", "m9ZeSk5AQ6et",
    "PuDk4whtk9U1", "eL8P89qQAYzT", "g3vDH5FXDDEo",
    "tx4LcT6vMTKT"]"""

hp1 = VPS("1Cbas2ZWQ8Kq", "Nathaniel Singer", "Healthy", 1651993737, "Ubuntu 20")
honeypots = ingest_honeypots("data/honeypots.yaml")

# Static routes
@app.route('/', methods=["GET"])
def root(): return redirect("dashboard", code=302)

@app.route('/login', methods=["GET"])
def login(): return render_template('login.html')

@app.route('/dashboard', methods=["GET"])
def dashboard(): return render_template('dashboard.html', count = len(honeypots), honeypots = honeypots)

@app.route('/stats', methods=["GET"])
def stats(): return render_template('stats.html')

@app.route('/statistics', methods=["GET"])
def statistics(): return redirect("dashboard", code=302)

@app.route('/about', methods=["GET"])
def about(): return render_template('about.html')


# Dynamic routes for static assets
@app.route('/static/<path:path>')
def send_report(path):
    return send_from_directory('static', path)


if __name__ == '__main__': app.run()