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
app.config['SECRET_KEY'] = 'super-secret-key-123'

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

# --- HTML Template (Embedded for 0-Error) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Mobile Lottery System</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://jsdelivr.net">
    <style>
        .hero { background: #6610f2; color: white; padding: 40px 0; border-radius: 0 0 50px 50px; }
        .card { border-radius: 15px; border: none; transition: 0.3s; }
        .card:hover { transform: translateY(-5px); }
        .price { font-size: 24px; color: #28a745; font-weight: bold; }
    </style>
</head>
<body class="bg-light">
    <div class="hero text-center mb-5 shadow">
        <h1>📱 Daily Mobile Lottery</h1>
        <p>Win Your Dream Phone | Every Day 8 PM Draw</p>
    </div>

    <div class="container">
        {% with messages = get_flashed_messages() %}
          {% if messages %}
            {% for message in messages %}
              <div class="alert alert-success shadow-sm text-center border-0">{{ message }}</div>
            {% endfor %}
          {% endif %}
        {% endwith %}

        <div class="row">
            {% for key, info in categories.items() %}
            <div class="col-md-4 mb-4">
                <div class="card shadow-sm p-4 text-center">
                    <h3 class="h5">{{ info.name }}</h3>
                    <p class="price">₹{{ info.price }}</p>
                    <form action="/buy/{{ key }}" method="POST">
                        <input type="text" name="name" placeholder="Full Name" class="form-control mb-2" required>
                        <input type="text" name="phone" placeholder="Phone Number" class="form-control mb-2" required>
                        <textarea name="address" placeholder="Delivery Address" class="form-control mb-2" rows="2" required></textarea>
                        <button type="submit" class="btn btn-primary w-100 shadow-sm">Buy Ticket</button>
                    </form>
                </div>
            </div>
            {% endfor %}
        </div>

        <div class="mt-5 mb-5 p-4 bg-white rounded shadow-sm">
            <h2 class="text-center mb-4">🏆 Recent Winners</h2>
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead class="table-light">
                        <tr><th>Date</th><th>Winner Name</th><th>Category</th><th>Ticket No</th></tr>
                    </thead>
                    <tbody>
                        {% for winner in winners %}
                        <tr>
                            <td>{{ winner.draw_date.strftime('%d-%m-%Y') }}</td>
                            <td>{{ winner.user_name }}</td>
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
    winners = Winner.query.order_by(Winner.draw_date.desc()).all()
    return render_template_string(HTML_TEMPLATE, categories=CATEGORIES, winners=winners)

@app.route('/buy/<cat_key>', methods=['POST'])
def buy_ticket(cat_key):
    name = request.form.get('name')
    phone = request.form.get('phone')
    address = request.form.get('address')
    t_num = random.randint(100000, 999999)
    
    new_ticket = Ticket(user_name=name, phone_number=phone, address=address, 
                        category=cat_key, ticket_number=t_num)
    db.session.add(new_ticket)
    db.session.commit()
    
    flash(f"Success! Ticket booked for {name}. No: {t_num}")
    return redirect(url_for('index'))

@app.route('/admin/draw')
def run_draw():
    for cat_key, info in CATEGORIES.items():
        tickets = Ticket.query.filter_by(category=cat_key).all()
        if tickets:
            winner_ticket = random.choice(tickets)
            new_winner = Winner(user_name=winner_ticket.user_name, 
                                category=info['name'], 
                                ticket_number=winner_ticket.ticket_number)
            db.session.add(new_winner)
            Ticket.query.filter_by(category=cat_key).delete()
    db.session.commit()
    return "Draw Finished! Go back to Home."

# --- Startup ---
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
