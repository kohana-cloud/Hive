from hashlib import new
from flask import Flask, render_template, redirect, send_from_directory, jsonify, request, Response
from flask_limiter.util import get_remote_address
from flask_limiter import Limiter
from src.code.Honeypots import ingest_honeypots
from src.code.Users import User, ingest_users, append_user, generate_pwhash
from functools import wraps
from src.code.gRPC.requests import query_for_honeypots, new_honeypot
import secrets, os, jwt, datetime, uuid
from flask_wtf.csrf import CSRFProtect
from flask_wtf.csrf import CSRFError
import time

HIVE_VERSION = "0.1b"
JQUERY_VERSION = "3.6.0"
BOOTSTRAP_VERSION = "5.1.3"
CHARTJS_VERSION = "3.8.0"


app = Flask(__name__, template_folder = os.path.abspath('src/pages'))
app.config['SECRET_KEY'] = str(secrets.randbits(256))
app.config['LOGINEXP_MINS'] = 30
app.config['BCRYPT_ROUNDS'] = 10
app.config['USER_CONFIG'] = "data/users.yaml"

limiter = Limiter(app, key_func = get_remote_address, default_limits=["20/minute", "200/hour"])
@app.errorhandler(429)
def ratelimit_handler(e):
    # TODO Log out user if logged in
    return render_template('rate-limit.html', jwt_name = ""), 429

csrf = CSRFProtect(app)
@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return render_template('csrf_error.html', jwt_name = ""), 403

app.config['USERS'] = ingest_users(app.config['USER_CONFIG'])
#app.config['HONEYPOTS'] = ingest_honeypots("data/honeypots.yaml")
app.config['HONEYPOTS'] = query_for_honeypots()
sessions = []


# Display secret
print(f"Secret: {app.config['SECRET_KEY']}")


# Decorators
def require_user(f):
    @wraps(f)
    def authenticate(*args, **kwargs):
        token, data = None, None

        # Retrieve and decode token, else error
        if ("Authentication" in request.cookies):
            token = request.cookies['Authentication'].split(" ")[1]
            
            try: data = jwt.decode(token, app.config['SECRET_KEY'], "HS256")
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
        # Get the first user where username or email matches
        try:
            user = [ user for user in app.config['USERS'] if
                (user.username == request.form['username']) or
                (user.email == request.form['username']) ][0]
        except IndexError:
            return render_template('login.html', invalid=True), 401

        # Validate Password
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
        print(token)
        bearer = f"Bearer {token}"

        # Respond
        rsp = redirect("/", 302)
        rsp.set_cookie("Authentication", bearer)
        return rsp

@app.route('/logout', methods=["GET"])
@require_user
@limiter.limit(None)
def logout(jwt_data):
    token, data = None, None

    # Retrieve and decode token, else error
    if ("Authentication" in request.cookies):
        token = request.cookies['Authentication'].split(" ")[1]
        
        try: data = jwt.decode(token, app.config['SECRET_KEY'], "HS256")
        except Exception as e: return f"Error: {e}", 403
    
    # Validate session based on authenticated user id from token
    if not (data['id'] in sessions): return redirect("login"), 403

    # Valid request, purge session and redirect
    sessions.remove(data['id'])
    return redirect("login"), 302

# TODO Need to actually add all the validation/RBAC stuff - Nate (nathaniel@singer.cloud)
@app.route('/adduser', methods=["POST"])
@limiter.limit(None)
def add_user():
    append_user(app.config['USER_CONFIG'], User(
        id = str(uuid.uuid1()),
        admin = False,
        username = request.form['user'],
        email = request.form['email'],
        pwhash_salted = generate_pwhash(
            request.form['password'], app.config['BCRYPT_ROUNDS']),
        first = request.form['firstname'],
        last = request.form['lastname'],
        phone = request.form['phone']
        ))

    # Update users in memory after append
    app.config['USERS'] = ingest_users(app.config['USER_CONFIG'])

    return redirect("login"), 302

@app.route('/dashboard', methods=["GET"])
@require_user
@limiter.limit(None)
def dashboard(jwt_data): return render_template('dashboard.html', count = len(app.config['HONEYPOTS']), honeypots = app.config['HONEYPOTS'], jwt_name = jwt_data['name'])

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
    if ("Authentication" in request.cookies):
        token = request.cookies['Authentication'].split(" ")[1]
        
        try: data = jwt.decode(token, app.config['SECRET_KEY'], "HS256")
        except Exception as e: return f"Error: {e}", 403

    else: return render_template('about.html', jwt_name = "",
        hive_v="", jquery_v="", bootstrap_v="", chart_v="")

    # Validate session based on authenticated user id from token
    if not (data['id'] in sessions): return render_template('about.html', jwt_name = "",
        hive_v="", jquery_v="", bootstrap_v="", chart_v="")

    # Deliver the page as authenticated
    return render_template('about.html', jwt_name = data['name'],
        hive_v=HIVE_VERSION, jquery_v=JQUERY_VERSION, bootstrap_v=BOOTSTRAP_VERSION, chart_v=CHARTJS_VERSION)


# Dynamic routes for assets
@app.route('/static/<path:path>')
@limiter.limit(None)
def send_report(path):
    return send_from_directory('static', path)


# API router (in development)
@csrf.exempt
@app.route('/api/v1/honeypots', methods=["GET", "POST"])
@require_user
@limiter.limit("120/minute;1200/hour", override_defaults=True)
def api_v1_honeypots(jwt_data):
    if (request.method == "GET"):
        return jsonify(app.config['HONEYPOTS'])
    elif (request.method == "POST"):
        new_honeypot()
        time.sleep(0.5)
        app.config['HONEYPOTS'] = query_for_honeypots()

        return 'success', 200


if __name__ == '__main__': app.run()