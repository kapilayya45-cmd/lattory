import os
import random
from datetime import datetime
from flask import Flask, request, redirect, url_for, flash, render_template_string, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# --- Configuration for Vercel ---
basedir = os.path.abspath(os.path.dirname(__file__))
# Vercel doesn't persist SQLite data, but this will let the app run
db_path = os.path.join(basedir, 'lottery.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'smart-win-vercel-pro-9121'

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
        .timer-box { background: rgba(255,255,255,0.03); border: 1px solid #00f2ff; padding: 12px 25px; border-radius: 50px; display: inline-block; margin-top: 15px; }
        #countdown { font-size: 1.6rem; font-weight: 800; color: #fff; }
        .card-split { background: #111; border: 1px solid #222; border-radius: 35px; overflow: hidden; margin-bottom: 40px; display: flex; flex-direction: row-reverse; transition: 0.4s; }
        .card-split:hover { border-color: #00f2ff; box-shadow: 0 0 30px rgba(0,242,255,0.15); }
        .img-side { flex: 1; background: #fff; display: flex; align-items: center; justify-content: center; padding: 25px; }
        .mobile-img { max-width: 100%; max-height: 380px; object-fit: contain; }
        .detail-side { flex: 1.2; padding: 45px; display: flex; flex-direction: column; justify-content: center; }
        .price-badge { background: #00f2ff; color: #000; padding: 6px 20px; border-radius: 50px; font-weight: 800; font-size: 1.3rem; width: fit-content; margin-bottom: 15px; box-shadow: 0 0 15px #00f2ff; }
        .form-control { background: #1a1a1a; border: 1px solid #333; color: #fff; border-radius: 12px; margin-bottom: 10px; }
        .btn-buy { background: #fff; color: #000; font-weight: 800; border-radius: 12px; padding: 15px; border: none; width: 100%; text-transform: uppercase; }
        .payment-alert { background: #111; border: 1px solid #28a745; color: #fff; border-radius: 25px; padding: 30px; margin-bottom: 40px; }
        @media (max-width: 992px) { .card-split { flex-direction: column; } .img-side { height: 300px; } }
        .whatsapp-float { position: fixed; bottom: 30px; right: 30px; background: #25d366; width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 30px; color: white; text-decoration: none; z-index: 1000; }
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
                <p>Scan QR to Pay Entry Fee & Confirm:</p>
                <div class="bg-white p-3 d-inline-block rounded-3 mb-3">
                    <img src="https://qrserver.com" alt="GPay QR">
                </div>
                <p class="text-secondary small">Send screenshot to WhatsApp: 9121195323</p>
            </div>
        {% endfor %}{% endif %}{% endwith %}

        {% for m in models %}
        <div class="card-split">
            <div class="img-side"><img src="{{ m.image_url }}" class="mobile-img"></div>
            <div class="detail-side">
                <div class="price-badge">₹{{ m.price }} ONLY</div>
                <h2 class="fw-bold mb-2" style="color: #00f2ff">{{ m.model_name }}</h2>
                <p class="text-secondary small mb-4" style="border-left: 3px solid #00f2ff; padding-left: 15px;">{{ m.specs }}</p>
                <form action="/buy/{{ m.category_key }}" method="POST">
                    <input name="name" placeholder="FULL NAME" class="form-control" required>
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
"""

# --- Routes ---
@app.route('/')
def index():
    models = MobileConfig.query.all()
    return render_template_string(USER_HTML, models=models)

@app.route('/buy/<cat>', methods=['POST'])
def buy(cat):
    t_num = random.randint(100000, 999999)
    new_t = Ticket(user_name=request.form['name'], phone_number=request.form['phone'], address=request.form['address'], category=cat, ticket_number=t_num)
    db.session.add(new_t)
    db.session.commit()
    flash(f"TICKET # {t_num} RESERVED SUCCESSFULLY!")
    return redirect('/')

# --- Database Startup for Vercel ---
with app.app_context():
    db.create_all()
    if not MobileConfig.query.first():
        configs = [
            MobileConfig(category_key='low_cost', model_name='Redmi 13C', specs='5000mAh Power', price=50, color='#00f2ff', image_url='https://media-amazon.com'),
            MobileConfig(category_key='mid_range', model_name='OnePlus Nord CE 4', specs='100W Charging', price=150, color='#00f2ff', image_url='https://media-amazon.com'),
            MobileConfig(category_key='flagship', model_name='iPhone 15 Pro', specs='Titanium Build', price=500, color='#00f2ff', image_url='https://media-amazon.com')
        ]
        db.session.bulk_save_objects(configs)
        db.session.commit()

# This is important for Vercel
app = app
