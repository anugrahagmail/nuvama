from flask import Flask, session, redirect, request, url_for, render_template_string
from flask_session import Session
import os
from APIConnect.APIConnect import APIConnect

app = Flask(__name__)

# Load secret key for Flask session from environment or default (change in production)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'change_me_to_a_secure_key')

# Use server-side sessions
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
Session(app)

# Nuvama API credentials from environment variables
NUVAMA_API_KEY = os.environ.get('NUVAMA_API_KEY')
NUVAMA_API_SECRET = os.environ.get('NUVAMA_API_SECRET')

# Base URL of your app, should be the same as Redirect URL registered with Nuvama
BASE_URL = os.environ.get('BASE_URL', 'https://app.theriskdiary.com')

# Construct the Nuvama login URL with proper redirect_uri pointing to your /login route
NuvamaLoginURL = (
    f"https://www.nuvamawealth.com/api-connect/login"
    f"?api_key={NUVAMA_API_KEY}&redirect_uri={BASE_URL}/login"
)

@app.route('/')
def index():
    if not session.get('requestId'):
        # No requestId means not logged in, redirect to login
        return redirect(url_for('login'))
    
    try:
        api = APIConnect(NUVAMA_API_KEY, NUVAMA_API_SECRET, session['requestId'], True)
        summary = api.GetSummary()
        trades = api.GetTrades()
    except Exception as e:
        return f"Error connecting to Nuvama API: {e}", 500

    return render_template_string("""
        <h1>Account Summary</h1>
        <pre>{{ summary }}</pre>
        <h2>Trades</h2>
        <pre>{{ trades }}</pre>
        <a href="{{ url_for('logout') }}">Logout</a>
    """, summary=summary, trades=trades)

@app.route('/login')
def login():
    request_id = request.args.get('request_id')
    if request_id:
        session['requestId'] = request_id
        try:
            api = APIConnect(NUVAMA_API_KEY, NUVAMA_API_SECRET, request_id, True)
            login_data = api.GetLoginData()  # Correct method to get login session details
        except Exception as e:
            return f"Login failed: {e}", 401
        return redirect(url_for('index'))
    else:
        return redirect(NuvamaLoginURL)

@app.route('/logout')
def logout():
    session.pop('requestId', None)
    return 'Logged out. <a href="/">Login again</a>'

@app.route('/health')
def health():
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
