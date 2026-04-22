import os
import random
from flask import Flask, request, redirect, url_for, render_template_string, flash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'smart-win-final-fixed-images-99'

# --- ఇమేజ్ ప్రాక్సీ ట్రిక్ (ఇది ఖచ్చితంగా ఫోటోలని చూపిస్తుంది) ---
def get_safe_img(url):
    # Jetpack Proxy logic
    return f"https://wp.com{url.replace('https://', '')}"

CATEGORIES = {
    'low_cost': {
        'name': 'Budget Kings', 
        'model': 'Moto G45 5G (Green)', 
        'specs': '50MP Camera | Vegan Leather | Snapdragon 6s Gen 3',
        'price': 50, 
        'color': '#00f2ff',
        'image_url': get_safe_img('://media-amazon.com')
    },
    'mid_range': {
        'name': 'Mid-Range Beasts', 
        'model': 'Samsung Galaxy M36 5G', 
        'specs': 'Circle to Search | Google Gemini AI | Victus+ Glass',
        'price': 150, 
        'color': '#b721ff',
        'image_url': get_safe_img('://media-amazon.com')
    },
    'flagship': {
        'name': 'Premium Flagships', 
        'model': 'iPhone 15 Pro', 
        'specs': 'Natural Titanium | A17 Pro Chip | 48MP Pro Lens',
        'price': 500, 
        'color': '#ff4b2b',
        'image_url': get_safe_img('://media-amazon.com')
    }
}

# --- UI Template (Ultra Stylish & Fixed Layout) ---
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
        .hero { padding: 40px 0; text-align: center; border-bottom: 1px solid #222; }
        .hero h1 { font-family: 'Syncopate', sans-serif; font-size: 2rem; color: #00f2ff; text-shadow: 0 0 10px #00f2ff; letter-spacing: 5px; }
        
        .timer-box { background: rgba(255,255,255,0.03); border: 1px solid #00f2ff; padding: 10px 20px; border-radius: 50px; display: inline-block; margin-top: 15px; }
        #countdown { font-size: 1.5rem; font-weight: 800; color: #fff; }

        /* SPLIT CARD DESIGN - Guaranteed No Overlap */
        .card-split { 
            background: #111; 
            border: 1px solid #222; 
            border-radius: 30px; 
            overflow: hidden; 
            margin-bottom: 40px; 
            display: flex; 
            flex-direction: row-reverse; /* Right: Image, Left: Details */
            flex-wrap: wrap; 
            transition: 0.3s;
        }
        .card-split:hover { border-color: #00f2ff; box-shadow: 0 0 30px rgba(0,242,255,0.1); }
        
        /* Image Side */
        .img-side { 
            flex: 1; 
            background: #fff; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            padding: 20px; 
            min-width: 300px; 
            min-height: 380px; 
        }
        .mobile-img { max-width: 100%; max-height: 350px; object-fit: contain; }
        
        /* Details Side */
        .detail-side { flex: 1.2; padding: 40px; display: flex; flex-direction: column; justify-content: center; min-width: 300px; }
        .price-badge { background: #00f2ff; color: #000; padding: 5px 20px; border-radius: 50px; font-weight: 800; font-size: 1.2rem; width: fit-content; margin-bottom: 15px; }
        
        /* Form Box Overlap Fix */
        .form-control { 
            background: #1a1a1a !important; 
            border: 1px solid #333 !important; 
            color: #fff !important; 
            border-radius: 12px !important; 
            padding: 12px !important;
            margin-bottom: 12px !important;
            display: block !important;
            width: 100% !important;
        }
        
        .btn-buy { background: #fff; color: #000; font-weight: 800; border-radius: 12px; padding: 15px; border: none; width: 100%; text-transform: uppercase; transition: 0.3s; }
        .btn-buy:hover { background: #00f2ff; transform: scale(1.02); }

        .payment-alert { background: #111; border: 1px solid #28a745; color: #fff; border-radius: 25px; padding: 30px; margin-bottom: 40px; }

        @media (max-width: 992px) { .card-split { flex-direction: column; } .img-side { min-height: 300px; } }
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
                <p class="mb-3">Scan QR & Send Screenshot to WhatsApp:</p>
                <div class="bg-white p-3 d-inline-block rounded-3 mb-3">
                    <img src="https://qrserver.com" alt="QR">
                </div>
                <p class="text-secondary small">WhatsApp: 9121195323</p>
            </div>
        {% endfor %}{% endif %}{% endwith %}

        {% for key, info in cats.items() %}
        <div class="card-split shadow">
            <!-- RIGHT SIDE: IMAGE (Proxied) -->
            <div class="img-side">
                <img src="{{ info.image_url }}" onerror="this.src='https://placeholder.com{{info.model}}'" class="mobile-img">
            </div>
            
            <!-- LEFT SIDE: DETAILS & FORM -->
            <div class="detail-side">
                <div class="price-badge">₹{{ info.price }} ONLY</div>
                <h2 class="fw-bold mb-2" style="color: #00f2ff">{{ info.model }}</h2>
                <p class="text-secondary small mb-4" style="border-left: 3px solid #00f2ff; padding-left: 15px;">{{ info.specs }}</p>
                <form action="/buy/{{ key }}" method="POST">
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

@app.route('/')
def index():
    return render_template_string(USER_HTML, cats=CATEGORIES)

@app.route('/buy/<cat>', methods=['POST'])
def buy(cat):
    t_num = random.randint(100000, 999999)
    flash(f"TICKET # {t_num} CONFIRMED! GOOD LUCK.")
    return redirect(url_for('index'))

app = app
