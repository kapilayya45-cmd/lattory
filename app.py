import os
import random
from flask import Flask, request, redirect, url_for, render_template_string, flash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'smart-win-final-999'

# --- IMAGE LINKS (Direct Public Links) ---
CATEGORIES = {
    'low_cost': {
        'name': 'Budget Kings', 
        'model': 'Redmi 13C', 
        'specs': '5000mAh Battery | 50MP AI Camera | 8GB RAM',
        'price': 50, 
        'color': '#00f2ff',
        # Google Image Proxy used here
        'image_url': 'https://weserv.nl'
    },
    'mid_range': {
        'name': 'Mid-Range Beasts', 
        'model': 'OnePlus Nord CE 4', 
        'specs': '100W Charging | AMOLED 120Hz | Sony Sensor',
        'price': 150, 
        'color': '#b721ff',
        'image_url': 'https://weserv.nl'
    },
    'flagship': {
        'name': 'Premium Flagships', 
        'model': 'iPhone 15 Pro', 
        'specs': 'Titanium Build | A17 Pro Chip | 48MP Pro Camera',
        'price': 500, 
        'color': '#ff4b2b',
        'image_url': 'https://weserv.nl'
    }
}

# --- UI Template (Absolute Layout Fix) ---
USER_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>SMART-WIN</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://jsdelivr.net">
    <style>
        @import url('https://googleapis.com');
        body { background: #050505; color: #fff; font-family: 'Inter', sans-serif; margin: 0; padding: 0; }
        .hero { padding: 40px 0; text-align: center; border-bottom: 1px solid #222; }
        .hero h1 { font-family: 'Syncopate', sans-serif; font-size: 2rem; color: #00f2ff; text-shadow: 0 0 10px #00f2ff; letter-spacing: 5px; }
        
        .timer-box { background: rgba(0,242,255,0.05); border: 1px solid #00f2ff; padding: 10px 25px; border-radius: 50px; display: inline-block; margin-top: 15px; }
        #countdown { font-size: 1.5rem; font-weight: 800; color: #fff; }

        /* SPLIT CARD FIX */
        .main-card { 
            background: #111; 
            border: 1px solid #222; 
            border-radius: 30px; 
            margin: 20px auto; 
            max-width: 900px; 
            overflow: hidden; 
            display: flex;
            flex-wrap: wrap; /* Fixed for Mobile */
        }

        .details-side { 
            flex: 1; 
            padding: 30px; 
            min-width: 300px;
        }

        .image-side { 
            flex: 1; 
            background: #ffffff; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            min-width: 300px; 
            min-height: 350px;
        }

        .mobile-img { width: 90%; height: auto; max-height: 320px; object-fit: contain; }

        .price-badge { background: #00f2ff; color: #000; padding: 5px 20px; border-radius: 50px; font-weight: 800; display: inline-block; margin-bottom: 15px; }
        
        /* FORM INPUT FIX (Strict Spacing) */
        .my-input { 
            background: #1a1a1a !important; 
            border: 1px solid #333 !important; 
            color: #fff !important; 
            border-radius: 12px !important; 
            padding: 12px !important; 
            width: 100% !important; 
            margin-bottom: 15px !important; 
            display: block !important;
        }

        .btn-buy { background: #fff; color: #000; font-weight: 800; border-radius: 12px; padding: 15px; border: none; width: 100%; text-transform: uppercase; margin-top: 10px; }
        
        @media (max-width: 768px) {
            .main-card { flex-direction: column-reverse; } /* Image on top for mobile */
            .image-side { min-height: 250px; }
        }
    </style>
</head>
<body>
    <div class="hero">
        <div class="container">
            <h1>SMART-WIN</h1>
            <div class="timer-box"><div id="countdown">00:00:00</div></div>
        </div>
    </div>

    <div class="container mt-4">
        {% with messages = get_flashed_messages() %}{% if messages %}{% for m in messages %}
            <div class="text-center p-4 mb-4" style="background:#111; border:1px solid #28a745; border-radius:20px;">
                <h4 class="text-success fw-bold">TICKET RESERVED!</h4>
                <p>{{m}}</p>
                <div class="bg-white p-2 d-inline-block rounded mb-2">
                    <img src="https://qrserver.com" alt="QR">
                </div>
                <p class="small text-secondary">Pay & WhatsApp Screenshot: 9121195323</p>
            </div>
        {% endfor %}{% endif %}{% endwith %}

        {% for key, info in cats.items() %}
        <div class="main-card shadow-lg">
            <!-- LEFT DETAILS -->
            <div class="details-side">
                <div class="price-badge">₹{{ info.price }} ONLY</div>
                <h2 style="color: {{info.color}}">{{ info.name }}</h2>
                <p class="small text-secondary mb-4" style="border-left: 3px solid #00f2ff; padding-left: 10px;">{{ info.specs }}</p>
                
                <form action="/buy/{{ key }}" method="POST">
                    <input name="name" placeholder="ENTER FULL NAME" class="my-input" required>
                    <input name="phone" placeholder="WHATSAPP NUMBER" class="my-input" required>
                    <textarea name="address" placeholder="DELIVERY ADDRESS" class="my-input" rows="2" required></textarea>
                    <button class="btn-buy">BOOK TICKET NOW</button>
                </form>
            </div>
            
            <!-- RIGHT IMAGE -->
            <div class="image-side">
                <img src="{{ info.image_url }}" onerror="this.src='https://placeholder.com...'" class="mobile-img">
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
    flash(f"Your Lucky Number: #{t_num}")
    return redirect(url_for('index'))

app = app
