import os
import random
from datetime import datetime
from flask import Flask, request, redirect, url_for, flash, render_template_string
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# --- Configuration ---
basedir = os.path.abspath(os.path.dirname(__file__))
# Railway storage fix: database path handling
db_path = os.path.join(basedir, 'lottery.db')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'smart-win-v4-fixed-99')

db = SQLAlchemy(app)

# --- Database Models ---
class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100))
    phone_number = db.Column(db.String(15))
    address = db.Column(db.Text)
    category = db.Column(db.String(50))
    ticket_number = db.Column(db.Integer, unique=True)

class Winner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100))
    category = db.Column(db.String(100))
    ticket_number = db.Column(db.Integer)
    draw_date = db.Column(db.DateTime, default=datetime.utcnow)

# --- Mobile Models & Specifications ---
CATEGORIES = {
    'low_cost': {
        'name': 'Budget Kings', 
        'model': 'Redmi 13C / Moto G34', 
        'specs': ['5000mAh Battery', '50MP AI Camera', '8GB RAM'],
        'price': 50, 
        'color': '#21d4fd'
    },
    'mid_range': {
        'name': 'Mid-Range Beasts', 
        'model': 'OnePlus Nord CE 4 / Realme 12 Pro', 
        'specs': ['100W Charging', 'Sony LYTIA Camera', 'AMOLED 120Hz'],
        'price': 150, 
        'color': '#b721ff'
    },
    'flagship': {
        'name': 'Premium Flagships', 
        'model': 'iPhone 15 / Galaxy S24 Ultra', 
        'specs': ['Titanium Body', '4K 60fps Video', 'Ultimate Gaming'],
        'price': 500, 
        'color': '#ff4b2b'
    }
}

# --- Professional UI Design (Embedded) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Smart-Win Mobile Lottery</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://jsdelivr.net">
    <link rel="stylesheet" href="https://cloudflare.com">
    <style>
        body { background: #0b0e14; color: #ffffff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .hero { padding: 60px 0; background: linear-gradient(180deg, rgba(33, 212, 253, 0.1) 0%, #0b0e14 100%); }
        .timer-box { font-size: 1.2rem; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); padding: 10px 25px; border-radius: 50px; color: #21d4fd; display: inline-block; margin-top: 20px; }
        .card-lottery { background: #161b22; border: 1px solid #30363d; border-radius: 24px; transition: 0.3s ease-in-out; position: relative; }
        .card-lottery:hover { transform: translateY(-10px); border-color: #58a6ff; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        .price-badge { position: absolute; top: -15px; right: 20px; background: #238636; color: white; padding: 5px 20px; border-radius: 12px; font-weight: 800; font-size: 1.4rem; z-index: 10; }
        .spec-list { list-style: none; padding: 0; font-size: 0.85rem; color: #8b949e; margin-bottom: 20px; }
        .spec-list li { margin-bottom: 5px; }
        .spec-list li i { color: #238636; margin-right: 8px; }
        .btn-buy { border-radius: 12px; font-weight: 700; padding: 12px; text-transform: uppercase; border: none; width: 100%; transition: 0.3s; color: white; }
        .winner-section { background: #161b22; border-radius: 24px; padding: 30px; border: 1px solid #30363d; }
    </style>
</head>
<body>
    <div class="hero text-center">
        <div class="container">
            <h1 class="fw-bold mb-2">Win Your Dream Mobile</h1>
            <p class="text-muted">Enter the lottery and get a chance to win premium devices daily.</p>
            <div class="timer-box" id="countdown">Loading Draw Timer...</div>
        </div>
    </div>
    <div class="container pb-5">
        {% with messages = get_flashed_messages() %}
          {% if messages %}
            {% for message in messages %}
              <div class="alert alert-success bg-success text-white border-0 rounded-3 text-center mb-4 shadow">{{ message }}</div>
            {% endfor %}
          {% endif %}
        {% endwith %}
        <div class="row">
            {% for key, info in categories.items() %}
            <div class="col-lg-4 col-md-6 mb-5">
                <div class="card card-lottery p-4 h-100 shadow">
                    <div class="price-badge">₹{{ info.price }}</div>
                    <div class="h3 mb-3" style="color: {{ info.color }};"><i class="fas fa-mobile-alt"></i></div>
                    <h3 class="fw-bold h5 mb-1">{{ info.name }}</h3>
                    <p class="small text-info mb-3">{{ info.model }}</p>
                    <ul class="spec-list">
                        {% for spec in info.specs %}
                        <li><i class="fas fa-check-circle"></i> {{ spec }}</li>
                        {% endfor %}
                    </ul>
                    <form action="/buy/{{ key }}" method="POST" class="mt-auto">
                        <input type="text" name="name" placeholder="Full Name" class="form-control bg-dark border-secondary text-white mb-2" required>
                        <input type="text" name="phone" placeholder="WhatsApp Number" class="form-control bg-dark border-secondary text-white mb-2" required>
                        <textarea name="address" placeholder="Shipping Address" class="form-control bg-dark border-secondary text-white mb-3" rows="2" required></textarea>
                        <button type="submit" class="btn-buy shadow" style="background: {{ info.color }};">Get Ticket Now</button>
                    </form>
                </div>
            </div>
            {% endfor %}
        </div>
        <div class="winner-section shadow mt-4">
            <h2 class="h4 mb-4 text-center"><i class="fas fa-trophy text-warning"></i> Recent Winners</h2>
            <div class="table-responsive">
                <table class="table table-dark table-hover border-0 mb-0">
                    <thead class="text-muted small uppercase">
                        <tr><th>Date</th><th>Winner</th><th>Device</th><th>Ticket</th></tr>
                    </thead>
                    <tbody>
                        {% for winner in winners %}
                        <tr class="align-middle">
                            <td>{{ winner.draw_date.strftime('%d %b') }}</td>
                            <td class="fw-bold">{{ winner.user_name }}</td>
                            <td><span class="badge bg-secondary">{{ winner.category }}</span></td>
                            <td class="text-info fw-bold">#{{ winner.ticket_number }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    <script>
        function updateTimer() {
            const now = new Date();
            const draw = new Date();
            draw.setHours(20, 0, 0, 0);
            if (now > draw) draw.setDate(draw.getDate() + 1);
            const diff = draw - now;
            const h = Math.floor(diff / 3600000);
            const m = Math.floor((diff % 3600000) / 60000);
            const s = Math.floor((diff % 60000) / 1000);
            document.getElementById('countdown').innerHTML = `<i class="far fa-clock"></i> Next Draw in: ${h}h ${m}m ${s}s`;
        }
        setInterval(updateTimer, 1000);
        updateTimer();
    </script>
</body>
</html>
"""

# --- Routes ---
@app.route('/')
def index():
    try:
        winners = Winner.query.order_by(Winner.draw_date.desc()).limit(10).all()
    except Exception:
        winners = []
    return render_template_string(HTML_TEMPLATE, categories=CATEGORIES, winners=winners)

@app.route('/buy/<cat_key>', methods=['POST'])
def buy_ticket(cat_key):
    name = request.form.get('name')
    phone = request.form.get('phone')
    address = request.form.get('address')
    t_num = random.randint(100000, 999999)
    
    try:
        new_ticket = Ticket(user_name=name, phone_number=phone, address=address, category=cat_key, ticket_number=t_num)
        db.session.add(new_ticket)
        db.session.commit()
        flash(f"🎉 Success, {name}! Your Ticket Number is #{t_num}")
    except Exception:
        db.session.rollback()
        flash("Error processing ticket. Please try again.")
        
    return redirect(url_for('index'))

# --- Database Startup Fix ---
with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        print(f"Database Init Error: {e}")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
