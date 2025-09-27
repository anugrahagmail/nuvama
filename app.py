from flask import Flask, session, redirect, request, render_template_string
from flask_session import Session
from APIConnect.APIConnect import APIConnect
import os
import requests

app = Flask(__name__)

# Secret key for encrypting session cookies, make this secure
app.secret_key = 'change_this_to_a_secure_random_key'

# Use filesystem for server-side sessions
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
Session(app)

NUVAMA_API_KEY = os.environ.get('NUVAMA_API_KEY')
NUVAMA_API_SECRET = os.environ.get('NUVAMA_API_SECRET')

NuvamaLoginURL = f"https://www.nuvamawealth.com/api-connect/login?api_key={NUVAMA_API_KEY}"

@app.route('/')
def index():
    if not session.get('requestId'):
        # Redirect user to Nuvama login URL to get requestId
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
    # This endpoint simulates user login step.
    # In real scenario, after redirect from Nuvama login page,
    # you receive requestId as query param, like ?requestId=abcdef
    request_id = request.args.get('requestId')
    if request_id:
        session['requestId'] = request_id
        return redirect('/')
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
    app.run(host='0.0.0.0', port=80)

