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
app.config['SECRET_KEY'] = 'professional-mobile-lottery-2024'

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

CATEGORIES = {
    'low_cost': {'name': 'Budget Mobiles', 'spec': 'Models Below 15k', 'price': 50, 'color': '#00d2ff'},
    'mid_range': {'name': 'Mid-Range Mobiles', 'spec': 'Models Below 40k', 'price': 150, 'color': '#9d50bb'},
    'flagship': {'name': 'Premium Flagships', 'spec': 'iPhone / S24 Ultra', 'price': 500, 'color': '#f21170'}
}

# --- Professional UI Design ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>NextGen Mobile Lottery</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://jsdelivr.net">
    <link rel="stylesheet" href="https://cloudflare.com">
    <style>
        :root { --glass: rgba(255, 255, 255, 0.1); }
        body { background: #0f0c29; background: linear-gradient(to right, #24243e, #302b63, #0f0c29); color: white; font-family: 'Inter', sans-serif; }
        
        .navbar { background: rgba(0,0,0,0.5); backdrop-filter: blur(10px); }
        .hero { padding: 80px 0 60px; text-align: center; }
        .hero h1 { font-size: 3.5rem; font-weight: 800; background: -webkit-linear-gradient(#eee, #333); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        
        .timer-box { background: var(--glass); border: 1px solid rgba(255,255,255,0.2); padding: 15px 30px; border-radius: 50px; display: inline-block; font-size: 1.5rem; font-weight: bold; color: #00d2ff; box-shadow: 0 0 20px rgba(0,210,255,0.3); }
        
        .card-lottery { background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 25px; backdrop-filter: blur(15px); transition: 0.4s; overflow: hidden; }
        .card-lottery:hover { transform: translateY(-15px); border-color: rgba(255,255,255,0.4); box-shadow: 0 20px 40px rgba(0,0,0,0.4); }
        
        .price-circle { width: 80px; height: 80px; line-height: 80px; background: white; color: black; border-radius: 50%; font-weight: 900; margin: -40px auto 20px; font-size: 1.2rem; box-shadow: 0 5px 15px rgba(0,0,0,0.2); }
        
        .btn-buy { border-radius: 12px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; padding: 12px; border: none; }
        
        .whatsapp-btn { position: fixed; bottom: 30px; right: 30px; width: 65px; height: 65px; background: #25d366; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 35px; color: white; text-decoration: none; box-shadow: 0 10px 25px rgba(37,211,102,0.4); z-index: 1000; }
        
        .table-custom { background: var(--glass); border-radius: 20px; color: white !important; }
        .table-custom th { color: #00d2ff; }
        .form-control { background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); color: white; }
        .form-control:focus { background: rgba(255,255,255,0.2); color: white; border-color: #00d2ff; box-shadow: none; }
    </style>
</head>
<body>

    <nav class="navbar navbar-dark fixed-top">
        <div class="container text-center">
            <a class="navbar-brand fw-bold" href="#"><i class="fas fa-bolt text-warning"></i> SMART-WIN LOTTERY</a>
        </div>
    </nav>

    <div class="hero">
        <div class="container">
            <h1>Dream Phones, Mini Prices.</h1>
            <p class="text-secondary mt-2">India's most transparent and automated mobile lottery system.</p>
            <div class="timer-box mt-4" id="countdown">Calculating Draw Time...</div>
        </div>
    </div>

    <div class="container mb-5">
        {% with messages = get_flashed_messages() %}
          {% if messages %}
            {% for message in messages %}
              <div class="alert alert-info bg-info text-dark border-0 rounded-pill text-center shadow-lg">{{ message }}</div>
            {% endfor %}
          {% endif %}
        {% endwith %}

        <div class="row mt-5">
            {% for key, info in categories.items() %}
            <div class="col-lg-4 mb-4">
                <div class="card card-lottery p-4 pt-5 text-center">
                    <div class="price-circle" style="background: {{ info.color }}; color: white;">₹{{ info.price }}</div>
                    <h3 class="fw-bold">{{ info.name }}</h3>
                    <p class="text-secondary small mb-4">{{ info.spec }}</p>
                    
                    <form action="/buy/{{ key }}" method="POST">
                        <input type="text" name="name" placeholder="Full Name" class="form-control mb-3" required>
                        <input type="text" name="phone" placeholder="WhatsApp Number" class="form-control mb-3" required>
                        <textarea name="address" placeholder="Shipping Address" class="form-control mb-4" rows="2" required></textarea>
                        <button type="submit" class="btn btn-buy w-100 shadow" style="background: {{ info.color }}; color: white;">Get Ticket Now</button>
                    </form>
                </div>
            </div>
            {% endfor %}
        </div>

        <!-- Recent Winners -->
        <div class="mt-5 p-5 card-lottery border-0 shadow">
            <h2 class="text-center mb-5 fw-bold"><i class="fas fa-award text-warning"></i> Recent Hall of Fame</h2>
            <div class="table-responsive">
                <table class="table table-custom table-hover border-0">
                    <thead class="text-center">
                        <tr><th>Date</th><th>Winner Name</th><th>Category</th><th>Ticket ID</th></tr>
                    </thead>
                    <tbody class="text-center align-middle">
                        {% for winner in winners %}
                        <tr>
                            <td>{{ winner.draw_date.strftime('%d %b, %Y') }}</td>
                            <td class="fw-bold">{{ winner.user_name }}</td>
                            <td><span class="badge bg-secondary">{{ winner.category }}</span></td>
                            <td><span class="text-info fw-bold">#{{ winner.ticket_number }}</span></td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <a href="https://wa.me" class="whatsapp-btn shadow-lg" target="_blank">
        <i class="fab fa-whatsapp"></i>
    </a>

    <script>
        function updateTimer() {
            const now = new Date();
            const drawTime = new Date();
            drawTime.setHours(20, 0, 0, 0); 
            if (now > drawTime) drawTime.setDate(drawTime.getDate() + 1);
            const diff = drawTime - now;
            const h = Math.floor((diff / (1000 * 60 * 60)) % 24);
            const m = Math.floor((diff / (1000 * 60)) % 60);
            const s = Math.floor((diff / 1000) % 60);
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
    except:
        winners = []
    return render_template_string(HTML_TEMPLATE, categories=CATEGORIES, winners=winners)

@app.route('/buy/<cat_key>', methods=['POST'])
def buy_ticket(cat_key):
    name = request.form.get('name')
    phone = request.form.get('phone')
    address = request.form.get('address')
    t_num = random.randint(100000, 999999)
    
    new_ticket = Ticket(user_name=name, phone_number=phone, address=address, category=cat_key, ticket_number=t_num)
    db.session.add(new_ticket)
    db.session.commit()
    
    flash(f"🎉 Awesome, {name}! Your ticket number is #{t_num}")
    return redirect(url_for('index'))

# --- Startup ---
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
