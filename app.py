import os
import random
from datetime import datetime
from flask import Flask, request, redirect, url_for, flash, render_template_string
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# --- Railway Configuration ---
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'lottery.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'lottery-super-secret-2024'

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
    'low_cost': {'name': 'Budget Mobiles (Below 10k)', 'price': 50},
    'mid_range': {'name': 'Mid-Range Mobiles (Above 10k)', 'price': 150},
    'flagship': {'name': 'Flagship Mobiles (High Cost)', 'price': 500}
}

# --- HTML Design with WhatsApp Button ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Mobile Lottery System</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://jsdelivr.net">
    <link rel="stylesheet" href="https://cloudflare.com">
    <style>
        body { background-color: #f4f7f6; font-family: 'Segoe UI', sans-serif; }
        .hero { background: linear-gradient(135deg, #6610f2, #6f42c1); color: white; padding: 50px 0; border-radius: 0 0 40px 40px; }
        .card { border-radius: 20px; border: none; transition: 0.3s; margin-bottom: 20px; }
        .card:hover { transform: translateY(-10px); box-shadow: 0 10px 20px rgba(0,0,0,0.1); }
        .price { font-size: 28px; color: #28a745; font-weight: bold; }
        .whatsapp-float {
            position: fixed; width: 60px; height: 60px; bottom: 40px; right: 40px;
            background-color: #25d366; color: #FFF; border-radius: 50px;
            text-align: center; font-size: 30px; box-shadow: 2px 2px 3px #999; z-index: 100;
        }
        .whatsapp-float:hover { background-color: #128c7e; color: white; }
        .badge-draw { background: #ffc107; color: #000; font-weight: bold; padding: 5px 15px; border-radius: 20px; }
    </style>
</head>
<body>
    <a href="https://wa.me, I want to join the lottery!" class="whatsapp-float" target="_blank">
        <i class="fab fa-whatsapp" style="margin-top:16px;"></i>
    </a>

    <div class="hero text-center mb-5 shadow">
        <h1>📱 Daily Mobile Lottery</h1>
        <p>Win Smartphones at Fraction of Price</p>
        <span class="badge-draw">Next Draw: 8:00 PM Tonight</span>
    </div>

    <div class="container">
        {% with messages = get_flashed_messages() %}
          {% if messages %}
            {% for message in messages %}
              <div class="alert alert-success shadow text-center">{{ message }}</div>
            {% endfor %}
          {% endif %}
        {% endwith %}

        <div class="row">
            {% for key, info in categories.items() %}
            <div class="col-md-4">
                <div class="card shadow-sm p-4 text-center">
                    <h3 class="h5">{{ info.name }}</h3>
                    <p class="price">₹{{ info.price }}</p>
                    <form action="/buy/{{ key }}" method="POST">
                        <input type="text" name="name" placeholder="Your Name" class="form-control mb-2" required>
                        <input type="text" name="phone" placeholder="WhatsApp Number" class="form-control mb-2" required>
                        <textarea name="address" placeholder="Shipping Address" class="form-control mb-2" rows="2" required></textarea>
                        <button type="submit" class="btn btn-primary w-100 fw-bold">BOOK TICKET</button>
                    </form>
                </div>
            </div>
            {% endfor %}
        </div>

        <div class="mt-5 mb-5 p-4 bg-white rounded shadow">
            <h2 class="text-center mb-4 text-primary"><i class="fas fa-trophy"></i> Recent Winners</h2>
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead class="table-light text-center">
                        <tr><th>Date</th><th>Winner</th><th>Category</th><th>Ticket ID</th></tr>
                    </thead>
                    <tbody class="text-center">
                        {% for winner in winners %}
                        <tr>
                            <td>{{ winner.draw_date.strftime('%d %b %Y') }}</td>
                            <td class="fw-bold">{{ winner.user_name }}</td>
                            <td>{{ winner.category }}</td>
                            <td><span class="badge bg-success">#{{ winner.ticket_number }}</span></td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
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
    return render_template_string(HTML_TEMPLATE, categories=CATEGORIES, winners=winners, whatsapp_num="91XXXXXXXXXX")

@app.route('/buy/<cat_key>', methods=['POST'])
def buy_ticket(cat_key):
    name = request.form.get('name')
    phone = request.form.get('phone')
    address = request.form.get('address')
    t_num = random.randint(100000, 999999)
    
    new_ticket = Ticket(user_name=name, phone_number=phone, address=address, category=cat_key, ticket_number=t_num)
    db.session.add(new_ticket)
    db.session.commit()
    
    flash(f"Booking Success! Ticket #{t_num} for {name}")
    return redirect(url_for('index'))

@app.route('/admin/draw')
def run_draw():
    # Only for admin to trigger winners
    for cat_key, info in CATEGORIES.items():
        tickets = Ticket.query.filter_by(category=cat_key).all()
        if tickets:
            winner_ticket = random.choice(tickets)
            new_winner = Winner(user_name=winner_ticket.user_name, category=info['name'], ticket_number=winner_ticket.ticket_number)
            db.session.add(new_winner)
            Ticket.query.filter_by(category=cat_key).delete()
    db.session.commit()
    return "Winners announced successfully!"

# --- App Initialize ---
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
