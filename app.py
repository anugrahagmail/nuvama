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

# Navigation panel to include in all pages
NAV_PANEL = """
<nav style="padding: 10px; background-color: #f0f0f0;">
    <a href="{{ url_for('index') }}">Home</a> |
    <a href="{{ url_for('orders') }}">Orders</a> |
    <a href="{{ url_for('trades') }}">Trades</a> |
    <a href="{{ url_for('positions') }}">Positions</a> |
    <a href="{{ url_for('holdings') }}">Holdings</a> |
    <a href="{{ url_for('limits') }}">Limits</a> |
    <a href="{{ url_for('funds') }}">Funds</a> |
    <a href="{{ url_for('logout') }}">Logout</a>
</nav>
<hr>
"""

# ----------------- Routes -----------------

@app.route('/')
def index():
    if not session.get('requestId'):
        return redirect(url_for('login'))

    return render_template_string(NAV_PANEL + """
        <h1>Welcome to Nuvama Dashboard</h1>
        <p>Select a feature from the navigation bar.</p>
    """)

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

# ----------------- API Pages -----------------

@app.route('/orders')
def orders():
    if not session.get('requestId'):
        return redirect(url_for('login'))

    try:
        api = APIConnect(NUVAMA_API_KEY, NUVAMA_API_SECRET, session['requestId'], True)
        orders = api.OrderBook()
    except Exception as e:
        return f"Error fetching orders: {e}", 500

    return render_template_string(NAV_PANEL + """
        <h1>Order Book</h1>
        <pre>{{ orders }}</pre>
    """, orders=orders)

@app.route('/trades')
def trades():
    if not session.get('requestId'):
        return redirect(url_for('login'))

    try:
        api = APIConnect(NUVAMA_API_KEY, NUVAMA_API_SECRET, session['requestId'], True)
        trades = api.TradeBook()
    except Exception as e:
        return f"Error fetching trades: {e}", 500

    return render_template_string(NAV_PANEL + """
        <h1>Trade Book</h1>
        <pre>{{ trades }}</pre>
    """, trades=trades)

@app.route('/positions')
def positions():
    if not session.get('requestId'):
        return redirect(url_for('login'))

    try:
        api = APIConnect(NUVAMA_API_KEY, NUVAMA_API_SECRET, session['requestId'], True)
        positions = api.PositionBook()
    except Exception as e:
        return f"Error fetching positions: {e}", 500

    return render_template_string(NAV_PANEL + """
        <h1>Positions</h1>
        <pre>{{ positions }}</pre>
    """, positions=positions)

@app.route('/holdings')
def holdings():
    if not session.get('requestId'):
        return redirect(url_for('login'))

    try:
        api = APIConnect(NUVAMA_API_KEY, NUVAMA_API_SECRET, session['requestId'], True)
        holdings = api.HoldingBook()
    except Exception as e:
        return f"Error fetching holdings: {e}", 500

    return render_template_string(NAV_PANEL + """
        <h1>Holdings</h1>
        <pre>{{ holdings }}</pre>
    """, holdings=holdings)

@app.route('/limits')
def limits():
    if not session.get('requestId'):
        return redirect(url_for('login'))

    try:
        api = APIConnect(NUVAMA_API_KEY, NUVAMA_API_SECRET, session['requestId'], True)
        limits = api.Limits()
    except Exception as e:
        return f"Error fetching limits: {e}", 500

    return render_template_string(NAV_PANEL + """
        <h1>Limits</h1>
        <pre>{{ limits }}</pre>
    """, limits=limits)

@app.route('/funds')
def funds():
    if not session.get('requestId'):
        return redirect(url_for('login'))

    try:
        api = APIConnect(NUVAMA_API_KEY, NUVAMA_API_SECRET, session['requestId'], True)
        funds = api.Funds()
    except Exception as e:
        return f"Error fetching funds: {e}", 500

    return render_template_string(NAV_PANEL + """
        <h1>Funds</h1>
        <pre>{{ funds }}</pre>
    """, funds=funds)

# ----------------- Run App -----------------

if __name__ == "__main__":
    # Keep host/port same as last working version for Lightsail subdomain
    app.run(host="0.0.0.0", port=5000)
