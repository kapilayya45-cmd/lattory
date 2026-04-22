import os
import random
from datetime import datetime
from flask import Flask, request, redirect, url_for, flash, render_template_string

app = Flask(__name__)
app.config['SECRET_KEY'] = 'smart-win-final-visual-fix'

# --- Reliable Image Links ---
CATEGORIES = {
    'low_cost': {
        'name': 'Budget Kings', 
        'model': 'Redmi 13C', 
        'specs': '5000mAh Battery | 50MP AI Camera | 8GB RAM',
        'price': 50, 
        'color': '#00f2ff',
        'image_url': 'https://media-amazon.com'
    },
    'mid_range': {
        'name': 'Mid-Range Beasts', 
        'model': 'OnePlus Nord CE 4', 
        'specs': '100W Charging | AMOLED 120Hz | Sony Camera',
        'price': 150, 
        'color': '#b721ff',
        'image_url': 'https://media-amazon.com'
    },
    'flagship': {
        'name': 'Premium Flagships', 
        'model': 'iPhone 15 Pro', 
        'specs': 'Titanium Build | A17 Pro Chip | 48MP Pro Lens',
        'price': 500, 
        'color': '#ff4b2b',
        'image_url': 'https://media-amazon.com'
    }
}

# --- Refined UI Template ---
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
        
        .hero { padding: 40px 0; text-align: center; border-bottom: 1px solid #222; }
        .hero h1 { font-family: 'Syncopate', sans-serif; font-size: 2rem; color: #00f2ff; text-shadow: 0 0 15px #00f2ff; letter-spacing: 5px; }
        
        .timer-box { background: rgba(255,255,255,0.03); border: 1px solid #00f2ff; padding: 10px 25px; border-radius: 50px; display: inline-block; margin-top: 10px; }
        #countdown { font-size: 1.5rem; font-weight: 800; color: #fff; }

        .card-split { background: #111; border: 1px solid #222; border-radius: 35px; overflow: hidden; margin-bottom: 40px; display: flex; flex-direction: row-reverse; transition: 0.4s; flex-wrap: wrap; }
        .card-split:hover { border-color: #00f2ff; box-shadow: 0 0 30px rgba(0,242,255,0.1); }
        
        /* Fixed Image Side */
        .img-side { flex: 1; background: #fff; display: flex; align-items: center; justify-content: center; padding: 20px; min-width: 300px; min-height: 380px; }
        .mobile-img { max-width: 100%; max-height: 350px; object-fit: contain; }
        
        /* Refined Details Side */
        .detail-side { flex: 1.2; padding: 40px; display: flex; flex-direction: column; justify-content: center; min-width: 300px; }
        .price-badge { background: #00f2ff; color: #000; padding: 6px 20px; border-radius: 50px; font-weight: 800; font-size: 1.2rem; width: fit-content; margin-bottom: 15px; box-shadow: 0 0 10px #00f2ff; }
        
        .mobile-name { font-weight: 800; font-size: 1.8rem; margin-bottom: 5px; }
        .spec-list { color: #888; font-size: 0.9rem; margin-bottom: 25px; border-left: 2px solid #00f2ff; padding-left: 15px; }

        /* Fixed Form Layout */
        .form-control { background: #1a1a1a; border: 1px solid #333; color: #fff; border-radius: 12px; margin-bottom: 12px; padding: 12px; font-size: 0.9rem; }
        .form-control:focus { background: #222; border-color: #00f2ff; color: #fff; box-shadow: none; }
        
        .btn-buy { background: #fff; color: #000; font-weight: 800; border-radius: 12px; padding: 15px; border: none; width: 100%; text-transform: uppercase; letter-spacing: 1px; transition: 0.3s; }
        .btn-buy:hover { background: #00f2ff; box-shadow: 0 0 20px #00f2ff; transform: scale(1.02); }

        @media (max-width: 992px) { .card-split { flex-direction: column; } .img-side { min-height: 250px; } .detail-side { padding: 30px; } }
        .whatsapp-float { position: fixed; bottom: 30px; right: 30px; background: #25d366; width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 30px; color: white; text-decoration: none; z-index: 1000; box-shadow: 0 0 20px rgba(0,0,0,0.3); }
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
        {% for key, info in cats.items() %}
        <div class="card-split">
            <!-- RIGHT SIDE: IMAGE -->
            <div class="img-side">
                <img src="{{ info.image_url }}" onerror="this.src='https://placeholder.com'" class="mobile-img">
            </div>
            
            <!-- LEFT SIDE: DETAILS & FORM -->
            <div class="detail-side">
                <div class="price-badge">₹{{ info.price }} ONLY</div>
                <h2 class="mobile-name" style="color: {{info.color}}">{{ info.name }}</h2>
                <p class="spec-list">{{ info.specs }}</p>
                
                <form action="/buy/{{ key }}" method="POST">
                    <input name="name" placeholder="ENTER YOUR FULL NAME" class="form-control" required>
                    <input name="phone" placeholder="WHATSAPP NUMBER" class="form-control" required>
                    <textarea name="address" placeholder="COMPLETE DELIVERY ADDRESS" class="form-control" rows="2" required></textarea>
                    <button class="btn-buy">BOOK MY TICKET NOW</button>
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

@app.route('/')
def index():
    return render_template_string(USER_HTML, cats=CATEGORIES)

@app.route('/buy/<cat>', methods=['POST'])
def buy(cat):
    return redirect(url_for('index'))

app = app
