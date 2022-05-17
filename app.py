from flask import Flask, render_template, redirect, send_from_directory, jsonify, request
from flask_limiter.util import get_remote_address
from flask_limiter import Limiter
from src.code.Honeypots import ingest_honeypots
from src.code.Users import ingest_users
import secrets
import os
import jwt

from functools import wraps


app = Flask(__name__, template_folder = os.path.abspath('src/pages'))

limiter = Limiter(app, key_func = get_remote_address, default_limits=["20/minute", "200/hour"])
@app.errorhandler(429)
def ratelimit_handler(e):
    # TODO Log out user if logged in
    return render_template('rate-limit.html'), 429


# Used for JWT validation
app.config['SECRET_KEY'] = str(secrets.randbits(256))
app.config['LOGINEXP_MINS'] = 30
app.config['BCRYPT_ROUNDS'] = 10

print(f"Secret: {app.config['SECRET_KEY']}")

users = ingest_users('data/users.yaml', app)
honeypots = ingest_honeypots("data/honeypots.yaml")




def require_user(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Retrieve token if it exists, else err
        if ("Authorization" in request.cookies):
            token = request.cookies['Authorization'].split(" ")[1]
        else: return redirect("login"), 302

        # Decode and verify signature
        try: 
            data = jwt.decode(token, app.config['SECRET_KEY'])

            user_index = [ i for i,user in enumerate(users) if user.id == data['id'] ][0]
            
            if (users[user_index].jwt is None): 
                return redirect("login"), 302
            
        except: return redirect("login"), 302

        return f(*args, **kwargs)
    
    return decorated


# Static routes
@app.route('/', methods=["GET"])
@limiter.limit(None)
def root(): return redirect("dashboard", code=302)

@app.route('/login', methods=["GET", "POST"])
@limiter.limit(None)
def login():
    invalid = False

    if request.method == 'POST':
        try: 
            # Get first user where username or email matches
            user = [ user for user in users if
                    (user.username == request.form['username']) or
                    (user.email == request.form['username']) ][0]

            # Validate password
            if (user.check_password(request.form['password'])):
                response = redirect("dashboard")
                response.set_cookie("Authorization", f"Bearer {user.get_jwt().decode('utf-8')}")
                return response

            else: invalid = True

        except IndexError: # User not found
            invalid = True
            
    return render_template('login.html', invalid=invalid)

@app.route('/logout', methods=["GET"])
@require_user
@limiter.limit(None)
def logout():    
    # Decode and verify signature
    token = request.cookies['Authorization'].split(" ")[1]
    data = jwt.decode(token, app.config['SECRET_KEY'])

    # Determine user by id and expire token
    user_index = [ i for i,user in enumerate(users) if user.id == data['id'] ][0]
    users[user_index].expire_jwt()

    return redirect("/login", code=302)
            

@app.route('/dashboard', methods=["GET"])
@require_user
@limiter.limit(None)
def dashboard(): return render_template('dashboard.html', count = len(honeypots), honeypots = honeypots)

@app.route('/profiler', methods=["GET"])
@require_user
@limiter.limit(None)
def profiler(): return render_template('profiler.html')

@app.route('/statistics', methods=["GET"])
@require_user
@limiter.limit(None)
def statistics(): return redirect("stats", code=302)

@app.route('/stats', methods=["GET"])
@require_user
@limiter.limit(None)
def stats(): return render_template('stats.html')

@app.route('/about', methods=["GET"])
@require_user
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
        'updated': 1652508781,
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
        'health': 1
    },
    '0ooQzs78Aizu': {
        'type': 'Database',
        'db-engine': 'mysql',
        'owner': 12345,
        'updated': 1651993737,
        'health': 0
    },
    '0SK8zO8VB8Wj': {
        'type': 'NAS',
        'owner': 12345,
        'updated': 1651123437,
        'health': 3
    },
    'qVAUYY6C67tv': {
        'type': 'Database',
        'db-engine': 'mysql',
        'owner': 12345,
        'updated': 1651933123,
        'health': 2
    },
    'yCdPU4EtIk33': {
        'type': 'NAS',
        'owner': 12345,
        'updated': 1652507693,
        'health': 0
    }
}

@app.route('/api/v1/honeypots', methods=["GET"])
@require_user
@limiter.limit("120/minute;1200/hour", override_defaults=True)
def api_v1_honeypots(): return jsonify(test_data)


if __name__ == '__main__': app.run()