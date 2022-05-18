from flask import Flask, render_template, redirect, send_from_directory, jsonify, request, Response
from flask_limiter.util import get_remote_address
from flask_limiter import Limiter
from src.code.Honeypots import ingest_honeypots
from src.code.Users import ingest_users
from functools import wraps
import secrets, os, jwt, datetime, time


app = Flask(__name__, template_folder = os.path.abspath('src/pages'))
app.config['SECRET_KEY'] = str(secrets.randbits(256))
app.config['LOGINEXP_MINS'] = 30
app.config['BCRYPT_ROUNDS'] = 10

limiter = Limiter(app, key_func = get_remote_address, default_limits=["20/minute", "200/hour"])
@app.errorhandler(429)
def ratelimit_handler(e):
    # TODO Log out user if logged in
    return render_template('rate-limit.html'), 429

users = ingest_users('data/users.yaml', app)
honeypots = ingest_honeypots("data/honeypots.yaml")
sessions = []


# Display secret
print(f"Secret: {app.config['SECRET_KEY']}")


# Decorators
def require_user(f):
    @wraps(f)
    def authenticate(*args, **kwargs):
        token, data = None, None

        # Retrieve and decode token, else error
        if ("Authorization" in request.cookies):
            token = request.cookies['Authorization'].split(" ")[1]
            
            try: data = jwt.decode(token, app.config['SECRET_KEY'])
            except Exception as e: return f"Error: {e}", 403

        else: return redirect("login"), 302

        # Validate session based on authenticated user id from token
        if not (data['id'] in sessions): return redirect("login"), 302

        # TODO Determine if token is close to experiation, regen if true

        # Return original request if authentication passes
        return f(data, *args, **kwargs)
    return authenticate


# Redirects
@app.route('/', methods=["GET"])
@limiter.limit(None)
def root(): return redirect("dashboard"), 302

@app.route('/statistics', methods=["GET"])
@limiter.limit(None)
def statistics(): return redirect("stats"), 302


# Static routes
@app.route('/login', methods=["GET", "POST"])
@limiter.limit(None)
def login():
    if (request.method == "GET"):
        return render_template('login.html', jwt_name = ""), 200

    # Receive and validate credentials
    if (request.method == "POST"):
        # Get the first user where username or email matches, validate pw
        try:
            user = [ user for user in users if
                (user.username == request.form['username']) or
                (user.email == request.form['username']) ][0]
        except IndexError:
            return render_template('login.html', invalid=True), 401

        if not (user.check_password(request.form['password'])):
            return render_template('login.html', invalid=True), 401
            
        # Force logout if login attempted with existing, else open new session
        if (user.id in sessions):
            return redirect("logout", 302)
        else: sessions.append(user.id)
        
        # Generate JWT
        token = jwt.encode({
            'id'    : user.id,
            'name'  : f"{user.first} {user.last}",
            'iss'   : "The Hive",
            'iat'   : datetime.datetime.utcnow(),
            'exp'   : datetime.datetime.utcnow() 
                       + datetime.timedelta(minutes = app.config['LOGINEXP_MINS'])
            }, app.config['SECRET_KEY'], "HS256")

        # Build bearer
        bearer = f"Bearer {token.decode('utf-8')}"

        # Respond
        rsp = redirect("/", 302)
        rsp.set_cookie("Authorization", bearer)
        return rsp

@app.route('/logout', methods=["GET"])
@require_user
@limiter.limit(None)
def logout(jwt_data):
    token, data = None, None

    # Retrieve and decode token, else error
    if ("Authorization" in request.cookies):
        token = request.cookies['Authorization'].split(" ")[1]
        
        try: data = jwt.decode(token, app.config['SECRET_KEY'])
        except Exception as e: return f"Error: {e}", 403
    
    # Validate session based on authenticated user id from token
    if not (data['id'] in sessions): return redirect("login"), 403

    # Valid request, purge session and redirect
    sessions.remove(data['id'])
    return redirect("login"), 302

@app.route('/dashboard', methods=["GET"])
@require_user
@limiter.limit(None)
def dashboard(jwt_data): return render_template('dashboard.html', count = len(honeypots), honeypots = honeypots, jwt_name = jwt_data['name'])

@app.route('/profiler', methods=["GET"])
@require_user
@limiter.limit(None)
def profiler(jwt_data): return render_template('profiler.html', jwt_name = jwt_data['name'])

@app.route('/stats', methods=["GET"])
@require_user
@limiter.limit(None)
def stats(jwt_data): return render_template('stats.html', jwt_name = jwt_data['name'])

@app.route('/about', methods=["GET"])
@limiter.limit(None)
def about():
    token, data = None, None
    
    # Retrieve and decode token, else error
    if ("Authorization" in request.cookies):
        token = request.cookies['Authorization'].split(" ")[1]
        
        try: data = jwt.decode(token, app.config['SECRET_KEY'])
        except Exception as e: return f"Error: {e}", 403

    else: return render_template('about.html', jwt_name = "")

    # Validate session based on authenticated user id from token
    if not (data['id'] in sessions):
        return render_template('about.html', jwt_name = "")

    # Deliver the page as authenticated
    return render_template('about.html', jwt_name = data['name'])


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
        'health': 3
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
def api_v1_honeypots(jwt_data): return jsonify(test_data)


if __name__ == '__main__': app.run()