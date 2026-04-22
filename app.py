import os
import random
from datetime import datetime
from flask import Flask, request, redirect, url_for, flash, render_template_string

app = Flask(__name__)
app.config['SECRET_KEY'] = 'smart-win-final-ultra-stylish-v11'

# --- ఇమేజ్ రావడానికి ప్రాక్సీ సర్వర్ వాడుతున్నాను (Guaranteed Fix) ---
def get_safe_url(img_url):
    return f"https://weserv.nl{img_url}&w=500&fit=contain&bg=white"

# --- మీ అమేజాన్ ఇమేజ్ లింక్స్ ఇక్కడ ఉన్నాయి ---
RAW_DATA = {
    'low_cost': {
        'name': 'Budget Kings', 
        'model': 'Redmi 13C', 
        'specs': '5000mAh Battery | 50MP AI Camera | 8GB RAM',
        'price': 50, 
        'color': '#00f2ff',
        'img': 'https://media-amazon.com'
    },
    'mid_range': {
        'name': 'Mid-Range Beasts', 
        'model': 'OnePlus Nord CE 4', 
        'specs': '100W Charging | AMOLED 120Hz | Sony Sensor',
        'price': 150, 
        'color': '#b721ff',
        'img': 'https://media-amazon.com'
    },
    'flagship': {
        'name': 'Premium Flagships', 
        'model': 'iPhone 15 Pro', 
        'specs': 'Titanium Build | A17 Pro Chip | 48MP Pro Camera',
        'price': 500, 
        'color': '#ff4b2b',
        'img': 'https://media-amazon.com'
    }
}

# Generate Proxy Links
CATEGORIES = {k: {**v, 'image_url': get_safe_url(v['img'])} for k, v in RAW_DATA.items()}

# --- UI Template (Forced Layout + Image Display) ---
USER_HTML = """
<!DOCTYPE html>
<html lang="te">
<head>
    <title>SMART-WIN | Ultra Modern</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://jsdelivr.net">
    <style>
        @import url('https://googleapis.com');
        
        body { background: #050505; color: #fff; font-family: 'Inter', sans-serif; overflow-x: hidden; }
        
        /* Header Section */
        .hero { padding: 40px 0; text-align: center; border-bottom: 1px solid #222; background: radial-gradient(circle at top, #111 0%, #050505 100%); }
        .hero h1 { font-family: 'Syncopate', sans-serif; font-size: 2rem; color: #00f2ff; text-shadow: 0 0 15px #00f2ff; letter-spacing: 5px; }
        
        .timer-box { background: rgba(255,255,255,0.03); border: 1px solid #00f2ff; padding: 10px 25px; border-radius: 50px; display: inline-block; margin-top: 15px; }
        #countdown { font-size: 1.5rem; font-weight: 800; color: #fff; }

        /* Split Card Design */
        .card-split { 
            background: #111; 
            border: 1px solid #222; 
            border-radius: 35px; 
            overflow: hidden; 
            margin-bottom: 40px; 
            display: flex; 
            flex-direction: row-reverse; /* Right: Image, Left: Detail */
            flex-wrap: wrap; 
        }
        
        /* Image Box - Pure White for Contrast */
        .img-side { 
            flex: 1; 
            background: #ffffff; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            padding: 30px; 
            min-width: 300px; 
            min-height: 400px; 
        }
        .mobile-img { max-width: 100%; max-height: 380px; object-fit: contain; }
        
        /* Detail Side */
        .detail-side { 
            flex: 1.2; 
            padding: 45px; 
            display: flex; 
            flex-direction: column; 
            justify-content: center; 
            min-width: 300px; 
        }
        .price-badge { background: #00f2ff; color: #000; padding: 6px 20px; border-radius: 50px; font-weight: 800; font-size: 1.3rem; width: fit-content; margin-bottom: 15px; }
        
        /* Form Box - Guaranteed No Overlap */
        .form-group { width: 100%; margin-bottom: 15px; }
        .form-control { 
            background: #1a1a1a !important; 
            border: 1px solid #333 !important; 
            color: #fff !important; 
            border-radius: 12px !important; 
            padding: 14px !important;
            display: block !important;
            width: 100% !important;
        }
        
        .btn-buy { background: #fff; color: #000; font-weight: 800; border-radius: 12px; padding: 15px; border: none; width: 100%; text-transform: uppercase; transition: 0.3s; margin-top: 10px; }
        .btn-buy:hover { background: #00f2ff; transform: scale(1.02); box-shadow: 0 0 20px #00f2ff; }

        .payment-alert { background: #111; border: 1px solid #28a745; color: #fff; border-radius: 25px; padding: 30px; margin-bottom: 40px; }

        @media (max-width: 992px) { 
            .card-split { flex-direction: column; } 
            .img-side { min-height: 300px; } 
        }

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
                    <img src="https://qrserver.com" alt="QR">
                </div>
                <p class="text-secondary small">Send screenshot to WhatsApp (9121195323) after payment.</p>
            </div>
        {% endfor %}{% endif %}{% endwith %}

        {% for key, info in cats.items() %}
        <div class="card-split">
            <!-- RIGHT SIDE: IMAGE -->
            <div class="img-side">
                <img src="{{ info.image_url }}" 
                     onerror="this.src='https://placeholder.com{{ info.model }}'" 
                     class="mobile-img">
            </div>
            
            <!-- LEFT SIDE: DETAILS & FORM -->
            <div class="detail-side">
                <div class="price-badge">₹{{ info.price }} ONLY</div>
                <h2 class="fw-bold mb-1" style="color: #00f2ff">{{ info.name }}</h2>
                <p class="text-secondary small mb-4" style="border-left: 3px solid #00f2ff; padding-left: 15px;">{{ info.specs }}</p>
                
                <form action="/buy/{{ key }}" method="POST">
                    <div class="form-group">
                        <input name="name" placeholder="ENTER FULL NAME" class="form-control" required>
                    </div>
                    <div class="form-group">
                        <input name="phone" placeholder="WHATSAPP NUMBER" class="form-control" required>
                    </div>
                    <div class="form-group">
                        <textarea name="address" placeholder="COMPLETE DELIVERY ADDRESS" class="form-control" rows="2" required></textarea>
                    </div>
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

@app.route('/')
def index():
    return render_template_string(USER_HTML, cats=CATEGORIES)

@app.route('/buy/<cat>', methods=['POST'])
def buy(cat):
    t_num = random.randint(100000, 999999)
    from flask import flash
    flash(f"మీ టికెట్ నంబర్: #{t_num}")
    return redirect(url_for('index'))

app = app
