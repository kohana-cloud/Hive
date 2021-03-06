from flask import Flask, render_template, redirect, send_from_directory, jsonify, request, Response
from flask_limiter.util import get_remote_address
from flask_limiter import Limiter
from flask_wtf.csrf import CSRFProtect, CSRFError
from functools import wraps
from hashlib import new
from src.code.configuration import Configuration

import secrets, os, jwt, datetime, uuid
import time

from src.code.Users import User, ingest_users, append_user, generate_pwhash
from src.code.gRPC.requests import query_honeypots, control_honeypot

## TODO Dynamic query for version information - Nate (nathaniel@singer.cloud)
HIVE_VERSION = "0.1b"
JQUERY_VERSION = "3.6.0"
BOOTSTRAP_VERSION = "5.1.3"
CHARTJS_VERSION = "3.8.0"


app = Flask(__name__, template_folder = os.path.abspath('src/pages'))

configuration = Configuration("configuration.yaml")
configuration.read_keys()

app.config['TLS_ENABLED'] = configuration.tls_enabled
app.config['PUBLIC_KEY'] = configuration.public_key

app.config['SECRET_KEY'] = str(secrets.randbits(256))
app.config['LOGINEXP_MINS'] = 120
app.config['BCRYPT_ROUNDS'] = 10
app.config['USER_CONFIG'] = "data/users.yaml"
app.config['USERS'] = ingest_users(app.config['USER_CONFIG'])

sessions = []


# Display secret
print(f"Secret: {app.config['SECRET_KEY']}")

# Start the APP
if __name__ == "__main__": app.run()



limiter = Limiter(app, key_func = get_remote_address, default_limits=["120/minute", "1000/hour"])
@app.errorhandler(429)
def ratelimit_handler(e):
    # TODO Log out user if logged in
    return render_template('rate-limit.html', jwt_name = ""), 429

csrf = CSRFProtect(app)
@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return render_template('csrf_error.html', jwt_name = ""), 403


# Decorators 
def require_user(f):
    @wraps(f)
    def authenticate(*args, **kwargs):
        token, data = None, None

        # Retrieve and decode token, else error
        if ("Authentication" in request.cookies):
            token = request.cookies['Authentication'].split(" ")[1]

            # If token is invalid, redirect to login
            try:
                data = jwt.decode(token, app.config['SECRET_KEY'], "HS256")
            except jwt.exceptions.ExpiredSignatureError:
                return render_template('login.html', invalid=True, login_error="Session expired, please login again!"), 302
            except Exception as e:
                print(f"JWT Error: {e}")
                return render_template('login.html', invalid=True, login_error="Unknown JWT error occured!"), 302

        else: return redirect("login"), 302

        # Validate session based on authenticated user id from token
        if not (data['id'] in sessions): return redirect("login"), 302

        # TODO Determine if token is close to experiation, regen if true - Nate (nathaniel@singer.cloud)

        # Return original request if authentication passes
        return f(data, *args, **kwargs)
    return authenticate


# Redirects
@app.route('/', methods=["GET"])
##@limiter.limit(None)
def root(): return redirect("dashboard"), 302


# Static routes
@app.route('/login', methods=["GET", "POST"])
#@limiter.limit(None)
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
            return render_template('login.html', invalid=True, login_error="Invalid credentials!"), 401

        # Validate Password
        if not (user.check_password(request.form['password'])):
            return render_template('login.html', invalid=True, login_error="Invalid credentials!"), 401
            
        # Add user to list of active sessions if not already existing
        if not (user.id in sessions): sessions.append(user.id)
        
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
        bearer = f"Bearer {token.decode('ascii')}"

        # Respond
        rsp = redirect("/", 302)
        rsp.set_cookie("Authentication", bearer)
        return rsp

@app.route('/logout', methods=["GET"])
@require_user
#@limiter.limit(None)
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
#@limiter.limit(None)
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
#@limiter.limit(None)
def dashboard(jwt_data):
    honeypots = query_honeypots(app.config['TLS_ENABLED'], app.config['PUBLIC_KEY'])
    return render_template('dashboard.html', count = len(honeypots), honeypots = honeypots, jwt_name = jwt_data['name'])

@app.route('/profiler', methods=["GET"])
@require_user
#@limiter.limit(None)
def profiler(jwt_data): return render_template('profiler.html', jwt_name = jwt_data['name'])

@app.route('/plotline', methods=["GET"])
@require_user
#@limiter.limit(None)
def stats(jwt_data): return render_template('plotline.html', jwt_name = jwt_data['name'])

@app.route('/about', methods=["GET"])
#@limiter.limit(None)
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
#@limiter.limit(None)
def send_report(path):
    return send_from_directory('static', path)


# API router (in development)
@csrf.exempt
@app.route('/api/v1/honeypots', methods=["GET"])
@require_user
#@limiter.limit("120/minute;1200/hour", override_defaults=True)
def api_v1_honeypots(jwt_data):
    return jsonify(query_honeypots(app.config['TLS_ENABLED'], app.config['PUBLIC_KEY']))


@csrf.exempt
@app.route('/api/v1/honeypot/create', methods=["GET", "POST"])
@require_user
#@limiter.limit("120/minute;1200/hour", override_defaults=True)
def api_v1_honeypot_create(jwt_data):
    # add the new honeypot if its a post
    if (request.method == "POST"):
        control_honeypot(f"create:{request.form['type']}", app.config['TLS_ENABLED'], app.config['PUBLIC_KEY'])

    return jsonify(query_honeypots(app.config['TLS_ENABLED'], app.config['PUBLIC_KEY']))


@csrf.exempt
@app.route('/api/v1/honeypot/delete', methods=["POST"])
@require_user
#@limiter.limit("120/minute;1200/hour", override_defaults=True)
def api_v1_honeypot_delete(jwt_data):
    # add the new honeypot if its a post
    if (request.method == "POST"):
        control_honeypot(f"delete:{request.form['hpid']}", app.config['TLS_ENABLED'], app.config['PUBLIC_KEY'])

    return jsonify(query_honeypots(app.config['TLS_ENABLED'], app.config['PUBLIC_KEY']))

@csrf.exempt
@app.route('/api/v1/honeypot/start', methods=["POST"])
@require_user
#@limiter.limit("120/minute;1200/hour", override_defaults=True)
def api_v1_honeypot_start(jwt_data):
    # add the new honeypot if its a post
    if (request.method == "POST"):
        control_honeypot(f"start:{request.form['hpid']}", app.config['TLS_ENABLED'], app.config['PUBLIC_KEY'])

    return jsonify(query_honeypots(app.config['TLS_ENABLED'], app.config['PUBLIC_KEY']))

@csrf.exempt
@app.route('/api/v1/honeypot/stop', methods=["POST"])
@require_user
##@limiter.limit("120/minute;1200/hour", override_defaults=True)
def api_v1_honeypot_stop(jwt_data):
    # add the new honeypot if its a post
    if (request.method == "POST"):
        control_honeypot(f"stop:{request.form['hpid']}", app.config['TLS_ENABLED'], app.config['PUBLIC_KEY'])

    return "Success", 200

@csrf.exempt
@app.route('/api/v1/honeypot/reset', methods=["POST"])
@require_user
##@limiter.limit("120/minute;1200/hour", override_defaults=True)
def api_v1_honeypot_reset(jwt_data):
    # add the new honeypot if its a post
    if (request.method == "POST"):
        control_honeypot(f"reset:{request.form['hpid']}", app.config['TLS_ENABLED'], app.config['PUBLIC_KEY'])

    return "Success", 200
    
@csrf.exempt
@app.route('/api/v1/honeypot/stopattack', methods=["POST"])
@require_user
##@limiter.limit("120/minute;1200/hour", override_defaults=True)
def api_v1_honeypot_stopattack(jwt_data):
    # add the new honeypot if its a post
    if (request.method == "POST"):
        control_honeypot(f"stopattack:{request.form['hpid']}", app.config['TLS_ENABLED'], app.config['PUBLIC_KEY'])

    return "Success", 200

