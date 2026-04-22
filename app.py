import os
import random
from datetime import datetime
from flask import Flask, request, redirect, url_for, flash, render_template_string, session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'smart-win-vercel-admin-9121'

# --- Categories Data (Direct Config) ---
CATEGORIES = {
    'low_cost': {
        'name': 'Budget Kings', 
        'model': 'Redmi 13C / Moto G34', 
        'specs': '5000mAh Battery | 50MP AI Camera',
        'price': 50, 
        'color': '#00f2ff',
        'image_url': 'https://media-amazon.com'
    },
    'mid_range': {
        'name': 'Mid-Range Beasts', 
        'model': 'OnePlus Nord CE 4', 
        'specs': '100W Charging | AMOLED 120Hz',
        'price': 150, 
        'color': '#b721ff',
        'image_url': 'https://media-amazon.com'
    },
    'flagship': {
        'name': 'Premium Flagships', 
        'model': 'iPhone 15 Pro', 
        'specs': 'Titanium Build | A17 Pro Chip',
        'price': 500, 
        'color': '#ff4b2b',
        'image_url': 'https://media-amazon.com'
    }
}

# --- UI Template ---
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
        body { background: #050505; color: #fff; font-family: 'Inter', sans-serif; }
        .hero { padding: 40px 0; text-align: center; border-bottom: 1px solid #222; }
        .hero h1 { font-family: 'Syncopate', sans-serif; font-size: 2.2rem; color: #00f2ff; text-shadow: 0 0 15px #00f2ff; letter-spacing: 5px; }
        .timer-box { background: rgba(255,255,255,0.03); border: 1px solid #00f2ff; padding: 12px 25px; border-radius: 50px; display: inline-block; margin-top: 15px; }
        #countdown { font-size: 1.6rem; font-weight: 800; color: #fff; }
        .card-split { background: #111; border: 1px solid #222; border-radius: 35px; overflow: hidden; margin-bottom: 40px; display: flex; flex-direction: row-reverse; }
        .img-side { flex: 1; background: #fff; display: flex; align-items: center; justify-content: center; padding: 25px; min-width: 300px; }
        .mobile-img { max-width: 100%; max-height: 350px; object-fit: contain; }
        .detail-side { flex: 1.2; padding: 45px; display: flex; flex-direction: column; justify-content: center; min-width: 300px; }
        .price-badge { background: #00f2ff; color: #000; padding: 6px 20px; border-radius: 50px; font-weight: 800; font-size: 1.3rem; width: fit-content; margin-bottom: 15px; }
        .form-control { background: #1a1a1a; border: 1px solid #333; color: #fff; border-radius: 12px; margin-bottom: 10px; }
        .btn-buy { background: #fff; color: #000; font-weight: 800; border-radius: 12px; padding: 15px; border: none; width: 100%; text-transform: uppercase; transition: 0.3s; }
        .btn-buy:hover { background: #00f2ff; box-shadow: 0 0 20px #00f2ff; }
        @media (max-width: 992px) { .card-split { flex-direction: column; } .img-side { height: 250px; } }
    </style>
</head>
<body>
    <div class="hero">
        <div class="container">
            <h1>SMART-WIN</h1>
            <div class="timer-box"><div id="countdown">00:00:00</div></div>
        </div>
    </div>
    <div class="container mt-5">
        {% with messages = get_flashed_messages() %}{% if messages %}{% for m in messages %}
            <div class="text-center p-4 mb-4" style="background:#111; border: 1px solid #28a745; border-radius:25px;">
                <h3 class="text-success">TICKET #{{ m }} RESERVED!</h3>
                <hr>
                <div class="bg-white p-3 d-inline-block rounded-3 mb-3">
                    <img src="https://qrserver.com" alt="QR">
                </div>
                <p>Scan & Pay. Then send screenshot to WhatsApp!</p>
                <a href="/admin" class="btn btn-sm btn-outline-secondary mt-3">Admin Login</a>
            </div>
        {% endfor %}{% endif %}{% endwith %}

        {% for key, info in cats.items() %}
        <div class="card-split shadow-lg">
            <div class="img-side"><img src="{{ info.image_url }}" class="mobile-img"></div>
            <div class="detail-side">
                <div class="price-badge">₹{{ info.price }} ONLY</div>
                <h2 class="fw-bold mb-2" style="color: #00f2ff">{{ info.name }}</h2>
                <p class="text-secondary small mb-4">{{ info.specs }}</p>
                <form action="/buy/{{ key }}" method="POST">
                    <input name="name" placeholder="FULL NAME" class="form-control" required>
                    <input name="phone" placeholder="WHATSAPP NUMBER" class="form-control" required>
                    <textarea name="address" placeholder="ADDRESS" class="form-control" rows="2" required></textarea>
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
    return render_template_string(USER_HTML, cats=CATEGORIES)

@app.route('/buy/<cat>', methods=['POST'])
def buy(cat):
    t_num = random.randint(100000, 999999)
    name = request.form.get('name')
    phone = request.form.get('phone')
    # Direct WhatsApp Notification Link (User will click this manually after booking)
    whatsapp_url = f"https://wa.me, I booked Ticket #{t_num} for {cat}. Name: {name}, Phone: {phone}"
    flash(str(t_num))
    return redirect(url_for('index'))

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if request.form.get('password') == 'admin123':
            session['logged_in'] = True
            return redirect('/admin')
    if not session.get('logged_in'):
        return render_template_string('<body style="background:#000;color:#fff;text-align:center;padding:100px;"><form method="POST">ADMIN KEY: <input name="password" type="password"><button>ENTER</button></form></body>')
    return render_template_string('<body style="background:#000;color:#fff;padding:50px;"><h2>Vercel Admin Active</h2><p>Data is handled via WhatsApp notifications.</p><a href="/logout" class="btn btn-danger">Logout</a></body>')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

app = app
