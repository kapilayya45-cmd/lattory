import os
import random
from datetime import datetime
from flask import Flask, request, redirect, url_for, flash, render_template_string, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# --- Configuration ---
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'lottery.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'ultra-futuristic-final-v2'

db = SQLAlchemy(app)

# --- Database Models ---
class MobileConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_key = db.Column(db.String(50), unique=True)
    model_name = db.Column(db.String(100))
    specs = db.Column(db.String(255))
    price = db.Column(db.Integer)
    color = db.Column(db.String(20))
    image_url = db.Column(db.String(500))

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100))
    phone_number = db.Column(db.String(15))
    address = db.Column(db.Text)
    category = db.Column(db.String(50))
    ticket_number = db.Column(db.Integer, unique=True)

# --- Ultra Stylish Split UI ---
USER_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>SMART-WIN | Ultra Modern</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://jsdelivr.net">
    <link rel="stylesheet" href="https://cloudflare.com">
    <style>
        @import url('https://googleapis.com');
        body { background: #050505; color: #fff; font-family: 'Inter', sans-serif; overflow-x: hidden; }
        
        .hero { padding: 60px 0; text-align: center; border-bottom: 1px solid #222; }
        .hero h1 { font-family: 'Syncopate', sans-serif; font-size: 2.2rem; color: #00f2ff; text-shadow: 0 0 15px #00f2ff; letter-spacing: 5px; }
        
        .timer-box { background: rgba(255,255,255,0.03); border: 1px solid #00f2ff; padding: 12px 25px; border-radius: 50px; display: inline-block; margin-top: 15px; box-shadow: 0 0 15px rgba(0,242,255,0.1); }
        #countdown { font-size: 1.6rem; font-weight: 800; color: #fff; }

        .card-split { background: #111; border: 1px solid #222; border-radius: 35px; overflow: hidden; margin-bottom: 40px; display: flex; flex-direction: row-reverse; transition: 0.4s; }
        .card-split:hover { border-color: #00f2ff; box-shadow: 0 0 30px rgba(0,242,255,0.15); transform: translateY(-5px); }
        
        .img-side { flex: 1; background: #fff; display: flex; align-items: center; justify-content: center; padding: 25px; }
        .mobile-img { max-width: 100%; max-height: 380px; object-fit: contain; filter: drop-shadow(0 5px 15px rgba(0,0,0,0.1)); }
        
        .detail-side { flex: 1.2; padding: 45px; display: flex; flex-direction: column; justify-content: center; }
        .price-badge { background: #00f2ff; color: #000; padding: 6px 20px; border-radius: 50px; font-weight: 800; font-size: 1.3rem; width: fit-content; margin-bottom: 15px; box-shadow: 0 0 15px #00f2ff; }
        
        .form-control { background: #1a1a1a; border: 1px solid #333; color: #fff; border-radius: 12px; margin-bottom: 10px; }
        .form-control:focus { background: #222; border-color: #00f2ff; box-shadow: none; color: #fff; }
        
        .btn-buy { background: #fff; color: #000; font-weight: 800; border-radius: 12px; padding: 15px; border: none; text-transform: uppercase; width: 100%; transition: 0.3s; }
        .btn-buy:hover { background: #00f2ff; box-shadow: 0 0 20px #00f2ff; transform: scale(1.02); }

        .payment-alert { background: #111; border: 1px solid #28a745; color: #fff; border-radius: 25px; padding: 30px; margin-bottom: 40px; box-shadow: 0 0 20px rgba(40,167,69,0.2); }

        @media (max-width: 992px) { .card-split { flex-direction: column; } .img-side { height: 300px; } }
        .whatsapp-float { position: fixed; bottom: 30px; right: 30px; background: #25d366; width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 30px; color: white; text-decoration: none; z-index: 1000; box-shadow: 0 10px 20px rgba(0,0,0,0.3); }
    </style>
</head>
<body>
    <a href="https://wa.me" class="whatsapp-float" target="_blank"><i class="fab fa-whatsapp"></i></a>

    <div class="hero">
        <div class="container">
            <h1>SMART-WIN</h1>
            <div class="timer-box"><div id="countdown">00:00:00</div></div>
        </div>
    </div>

    <div class="container mt-5">
        {% with messages = get_flashed_messages() %}{% if messages %}{% for m in messages %}
            <div class="payment-alert text-center shadow-lg">
                <h3 class="text-success fw-bold">🎉 TICKET RESERVED!</h3>
                <p>{{m}}</p>
                <hr style="border-color: #333;">
                <p class="mb-3">Scan QR to Pay Entry Fee & Confirm:</p>
                <div class="bg-white p-3 d-inline-block rounded-3 mb-3">
                    <img src="https://qrserver.com" alt="GPay QR">
                </div>
                <p class="text-secondary small">Send screenshot to WhatsApp after payment.</p>
            </div>
        {% endfor %}{% endif %}{% endwith %}

        {% for m in models %}
        <div class="card-split">
            <div class="img-side">
                <img src="{{ m.image_url }}" onerror="this.src='https://placeholder.com{{m.model_name}}'" class="mobile-img">
            </div>
            <div class="detail-side">
                <div class="price-badge">₹{{ m.price }} ONLY</div>
                <h2 class="fw-bold mb-2" style="color: #00f2ff">{{ m.model_name }}</h2>
                <p class="text-secondary small mb-4" style="border-left: 3px solid #00f2ff; padding-left: 15px;">{{ m.specs }}</p>
                <form action="/buy/{{ m.category_key }}" method="POST">
                    <input name="name" placeholder="ENTER FULL NAME" class="form-control" required>
                    <input name="phone" placeholder="WHATSAPP NUMBER" class="form-control" required>
                    <textarea name="address" placeholder="COMPLETE ADDRESS" class="form-control" rows="2" required></textarea>
                    <button class="btn-buy">BOOK & PAY NOW</button>
                </form>
            </div>
        </div>
        {% endfor %}
    </div>

    <script>
        function updateTimer() {
            const now = new Date();
            const draw = new Date(); draw.setHours(20, 0, 0, 0); 
            if (now > draw) draw.setDate(draw.getDate() + 1);
            const diff = draw - now;
            const h = String(Math.floor(diff / 3600000)).padStart(2, '0');
            const m = String(Math.floor((diff % 3600000) / 60000)).padStart(2, '0');
            const s = String(Math.floor((diff % 60000) / 1000)).padStart(2, '0');
            document.getElementById('countdown').innerHTML = h + ":" + m + ":" + s;
        }
        setInterval(updateTimer, 1000); updateTimer();
    </script>
</body>
</html>
