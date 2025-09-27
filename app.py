from flask import Flask, session, redirect, request, render_template_string, url_for
from flask_session import Session
import os
from APIConnect.APIConnect import APIConnect

app = Flask(__name__)

# Secret key for encrypting session cookies, make this secure
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'change_this_to_a_secure_random_key')

# Use filesystem for server-side sessions
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
Session(app)

NUVAMA_API_KEY = os.environ.get('NUVAMA_API_KEY')
NUVAMA_API_SECRET = os.environ.get('NUVAMA_API_SECRET')

# Base URL of your deployed app (must be set as environment variable)
BASE_URL = os.environ.get('BASE_URL', 'https://app.theriskdiary.com')

# Construct Nuvama login URL with redirect_uri to your public domain
NuvamaLoginURL = f"https://www.nuvamawealth.com/api-connect/login?api_key={NUVAMA_API_KEY}&redirect_uri={BASE_URL}/login"

@app.route('/')
def index():
    if not session.get('requestId'):
        # Redirect user to login page which handles Nuvama login URL redirect
        return redirect('/login')

    # Have requestId, initiate session with Nuvama API
    api = APIConnect(NUVAMA_API_KEY, NUVAMA_API_SECRET, session['requestId'], True)
    api.Init()

    summary = api.GetSummary()
    trades = api.GetTrades()

    return render_template_string("""
        <h1>Account Summary</h1>
        <pre>{{ summary }}</pre>
        <h2>Trades</h2>
        <pre>{{ trades }}</pre>
        <a href="/logout">Logout</a>
    """, summary=summary, trades=trades)

@app.route('/login')
def login():
    # Handle login redirect from Nuvama with requestId as query param
    request_id = request.args.get('requestId')
    if request_id:
        session['requestId'] = request_id
        # Redirect to home page now that requestId is saved in session
        return redirect(url_for('index'))
    else:
        # Redirect user to Nuvama login page to authenticate and get requestId
        return redirect(NuvamaLoginURL)

@app.route('/logout')
def logout():
    session.pop('requestId', None)
    return 'Logged out. <a href="/">Login again</a>'

@app.route('/health')
def health():
    return "OK", 200

if __name__ == '__main__':
    # Run on all interfaces, port 80 or 8000 depending on your deployment
    app.run(host='0.0.0.0', port=80)
