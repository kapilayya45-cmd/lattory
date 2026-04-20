import os
import random
from datetime import datetime
from flask import Flask, request, redirect, url_for, flash, render_template_string
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# --- Configuration ---
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'lottery.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'mobile-lottery-v3-pro'

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

# --- Professional UI Design ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Smart-Win Mobile Lottery</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://jsdelivr.net">
    <link rel="stylesheet" href="https://cloudflare.com">
    <style>
        body { background: #0b0e14; color: #ffffff; font-family: 'Poppins', sans-serif; }
        .hero { padding: 60px 0; background: linear-gradient(180deg, rgba(33, 212, 253, 0.1) 0%, #0b0e14 100%); }
        .hero h1 { font-weight: 800; font-size: 2.8rem; letter-spacing: -1px; }
        
        .timer-box { font-size: 1.2rem; background: rgba(255,255,255,0.05); border: 1px border: 1px solid rgba(255,255,255,0.1); padding: 10px 25px; border-radius: 50px; color: #21d4fd; display: inline-block; margin-top: 20px; }
        
        .card-lottery { background: #161b22; border: 1px solid #30363d; border-radius: 24px; transition: 0.3s ease-in-out; position: relative; overflow: visible; }
        .card-lottery:hover { transform: translateY(-10px); border-color: #58a6ff; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        
        /* Price Badge Fix */
        .price-badge { position: absolute; top: -15px; right: 20px; background: #238636; color: white; padding: 5px 20px; border-radius: 12px; font-weight: 800; font-size: 1.4rem; box-shadow: 0 4px 15px rgba(0,0,0,0.3); z-index: 10; }
        
        .mobile-icon { font-size: 3rem; margin-bottom: 15px; opacity: 0.8; }
        .spec-list { list-style: none; padding: 0; font-size: 0.85rem; color: #8b949e; margin-bottom: 20px; }
        .spec-list li { margin-bottom: 5px; }
        .spec-list li i { color: #238636; margin-right: 8px; }
        
        .form-control { background: #0d1117; border: 1px solid #30363d; color: white; border-radius: 10px; }
        .form-control:focus { background: #0d1117; color: white; border-color: #58a6ff; box-shadow: none; }
        .btn-buy { border-radius: 12px; font-weight: 700; padding: 12px; text-transform: uppercase; border: none; width: 100%; transition: 0.3s; }
        .btn-buy:hover { opacity: 0.9; transform: scale(1.02); }

        .winner-section { background: #161b22; border-radius: 24px; padding: 30px; border: 1px solid #30363d; }
        .whatsapp-float { position: fixed; bottom: 30px; right: 30px; background: #25d366; width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 30px; color: white; text-decoration: none; box-shadow: 0 10px 20px rgba(0,0,0,0.3); z-index: 1000; }
    </style>
</head>
<body>

    <div class="hero text-center">
        <div class="container">
            <h1 class="mb-2 text-white">Win Your Dream Mobile</h1>
            <p class="text-muted">Enter the lottery and get a chance to win premium devices daily.</p>
            <div class="timer-box" id="countdown">Loading Timer...</div>
        </div>
    </div>

    <div class="container pb-5">
        {% with messages = get_flashed_messages() %}
          {% if messages %}
            {% for message in messages %}
              <div class="alert alert-success bg-success text-white border-0 rounded-3 text-center mb-4">{{ message }}</div>
            {% endfor %}
          {% endif %}
        {% endwith %}

        <div class="row">
            {% for key, info in categories.items() %}
            <div class="col-lg-4 col-md-6 mb-5">
                <div class="card card-lottery p-4 h-100">
                    <div class="price-badge">₹{{ info.price }}</div>
                    <div class="mobile-icon" style="color: {{ info.color }};"><i class="fas fa-mobile-alt"></i></div>
                    <h3 class="fw-bold h5 mb-1">{{ info.name }}</h3>
                    <p class="small text-info mb-3">{{ info.model }}</p>
                    
                    <ul class="spec-list">
                        {% for spec in info.specs %}
                        <li><i class="fas fa-check-circle"></i> {{ spec }}</li>
                        {% endfor %}
                    </ul>
                    
                    <form action="/buy/{{ key }}" method="POST" class="mt-auto">
                        <input type="text" name="name" placeholder="Full Name" class="form-control mb-2" required>
                        <input type="text" name="phone" placeholder="WhatsApp Number" class="form-control mb-2" required>
                        <textarea name="address" placeholder="Shipping Address" class="form-control mb-3" rows="2" required></textarea>
                        <button type="submit" class="btn-buy shadow" style="background: {{ info.color }}; color: white;">Get Ticket</button>
                    </form>
                </div>
            </div>
            {% endfor %}
        </div>

        <div class="winner-section shadow">
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
                            <td class="text-info">#{{ winner.ticket_number }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <a href="https://wa.me" class="whatsapp-float" target="_blank"><i class="fab fa-whatsapp"></i></a>

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
