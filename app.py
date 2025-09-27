from flask import Flask, session, redirect, request, url_for, render_template_string
from flask_session import Session
import os
import logging
from APIConnect.APIConnect import APIConnect

# -----------------------
# Flask Setup
# -----------------------
app = Flask(__name__)

# Secret key for sessions (use environment variable in production)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'change_me_to_a_secure_key')

# Server-side sessions
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
Session(app)

# -----------------------
# Logging Setup
# -----------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -----------------------
# Nuvama API Config
# -----------------------
NUVAMA_API_KEY = os.environ.get('NUVAMA_API_KEY')
NUVAMA_API_SECRET = os.environ.get('NUVAMA_API_SECRET')
BASE_URL = os.environ.get('BASE_URL', 'https://app.theriskdiary.com')

if not NUVAMA_API_KEY or not NUVAMA_API_SECRET:
    logger.error("NUVAMA_API_KEY or NUVAMA_API_SECRET is missing!")

# Construct login URL
NuvamaLoginURL = (
    f"https://www.nuvamawealth.com/api-connect/login"
    f"?api_key={NUVAMA_API_KEY}&redirect_uri={BASE_URL}/login"
)

# -----------------------
# Routes
# -----------------------
@app.route('/')
def index():
    if not session.get('requestId'):
        # Not logged in, redirect to login
        return redirect(url_for('login'))

    try:
        api = APIConnect(NUVAMA_API_KEY, NUVAMA_API_SECRET, session['requestId'], True)
        api.Init()
        summary = api.GetSummary()
        trades = api.GetTrades()
    except Exception as e:
        logger.exception("Failed to fetch account data from Nuvama API")
        return render_template_string("""
            <h1>Error connecting to Nuvama API</h1>
            <p>{{ error }}</p>
            <a href="{{ url_for('logout') }}">Logout</a>
        """, error=str(e)), 500

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
            login_data = api.GetLoginData()
            logger.info(f"Login successful: {login_data}")
        except Exception as e:
            logger.exception("Login failed")
            return render_template_string("""
                <h1>Login Failed</h1>
                <p>{{ error }}</p>
                <a href="{{ url_for('login') }}">Try again</a>
            """, error=str(e)), 401
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


# -----------------------
# Run App
# -----------------------
if __name__ == "__main__":
    # Enable debug=True to see Flask error trace in browser
    app.run(host="0.0.0.0", port=5000, debug=True)
