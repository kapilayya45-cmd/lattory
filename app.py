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
app.config['SECRET_KEY'] = 'admin-secret-999'

db = SQLAlchemy(app)

# --- Database Models ---
class MobileConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_key = db.Column(db.String(50), unique=True) # low_cost, mid_range, flagship
    model_name = db.Column(db.String(100))
    specs = db.Column(db.String(255)) # Comma separated specs
    price = db.Column(db.Integer)
    color = db.Column(db.String(20))

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100))
    phone_number = db.Column(db.String(15))
    address = db.Column(db.Text)
    category = db.Column(db.String(50))
    ticket_number = db.Column(db.Integer, unique=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Winner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100))
    category = db.Column(db.String(100))
    ticket_number = db.Column(db.Integer)
    draw_date = db.Column(db.DateTime, default=datetime.utcnow)

# --- Initial Data Setup ---
def init_data():
    with app.app_context():
        db.create_all()
        if not MobileConfig.query.first():
            configs = [
                MobileConfig(category_key='low_cost', model_name='Redmi 13C', specs='5000mAh, 50MP, 8GB', price=50, color='#21d4fd'),
                MobileConfig(category_key='mid_range', model_name='OnePlus Nord', specs='100W Charging, AMOLED', price=150, color='#b721ff'),
                MobileConfig(category_key='flagship', model_name='iPhone 15', specs='Titanium, 4K Video', price=500, color='#ff4b2b')
            ]
            db.session.bulk_save_objects(configs)
            db.session.commit()

# --- UI TEMPLATES ---
NAVBAR = """<nav class="navbar navbar-dark bg-dark mb-4 shadow"><div class="container"><a class="navbar-brand fw-bold" href="/">SMART-WIN</a><a class="btn btn-outline-info btn-sm" href="/admin">Admin Login</a></div></nav>"""

USER_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Smart-Win Mobile Lottery</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://jsdelivr.net">
    <link rel="stylesheet" href="https://cloudflare.com">
    <style>
        body { background: #0b0e14; color: white; font-family: 'Segoe UI', sans-serif; }
        .card-lottery { background: #161b22; border: 1px solid #30363d; border-radius: 20px; position: relative; margin-bottom: 30px; }
        .price-badge { position: absolute; top: -15px; right: 15px; background: #238636; padding: 5px 15px; border-radius: 10px; font-weight: bold; }
    </style>
</head>
<body>
    """ + NAVBAR + """
    <div class="container text-center mb-5">
        <h1 class="fw-bold">Win Premium Mobiles Daily</h1>
        <p class="text-muted">Select a category and book your ticket.</p>
    </div>
    <div class="container">
        {% with messages = get_flashed_messages() %}{% if messages %}{% for m in messages %}<div class="alert alert-success text-center">{{m}}</div>{% endfor %}{% endif %}{% endwith %}
        <div class="row">
            {% for m in models %}
            <div class="col-md-4">
                <div class="card card-lottery p-4 h-100">
                    <div class="price-badge">₹{{ m.price }}</div>
                    <h3 style="color: {{m.color}}">{{ m.model_name }}</h3>
                    <p class="small text-muted">{{ m.specs }}</p>
                    <form action="/buy/{{ m.category_key }}" method="POST" class="mt-auto">
                        <input name="name" placeholder="Name" class="form-control bg-dark text-white mb-2" required>
                        <input name="phone" placeholder="WhatsApp" class="form-control bg-dark text-white mb-2" required>
                        <textarea name="address" placeholder="Address" class="form-control bg-dark text-white mb-3" required></textarea>
                        <button class="btn w-100 fw-bold text-white" style="background: {{m.color}}">GET TICKET</button>
                    </form>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
"""

ADMIN_HTML = """
<!DOCTYPE html>
<html>
<head><title>Admin Panel</title><link rel="stylesheet" href="https://jsdelivr.net"></head>
<body class="bg-light text-dark">
    <div class="container mt-5">
        <h2>Admin Dashboard <a href="/logout" class="btn btn-danger btn-sm float-end">Logout</a></h2>
        <hr>
        <div class="row">
            <div class="col-md-8">
                <h4>Active Tickets</h4>
                <table class="table table-bordered bg-white">
                    <thead><tr><th>Name</th><th>Phone</th><th>Category</th><th>Ticket</th></tr></thead>
                    <tbody>
                        {% for t in tickets %}
                        <tr><td>{{t.user_name}}</td><td>{{t.phone_number}}</td><td>{{t.category}}</td><td>#{{t.ticket_number}}</td></tr>
                        {% endfor %}
                    </tbody>
                </table>
                <a href="/admin/draw" class="btn btn-warning fw-bold">RUN DRAW (Pick Winners)</a>
            </div>
            <div class="col-md-4">
                <h4>Update Mobiles</h4>
                {% for m in models %}
                <form action="/admin/update/{{m.category_key}}" method="POST" class="card p-3 mb-3 shadow-sm">
                    <label>{{ m.category_key }}</label>
                    <input name="model" value="{{m.model_name}}" class="form-control mb-1">
                    <input name="specs" value="{{m.specs}}" class="form-control mb-1">
                    <input name="price" value="{{m.price}}" class="form-control mb-1">
                    <button class="btn btn-primary btn-sm mt-1">Update</button>
                </form>
                {% endfor %}
            </div>
        </div>
    </div>
</body>
</html>
"""

# --- Routes ---
@app.route('/')
def index():
    models = MobileConfig.query.all()
    winners = Winner.query.all()
    return render_template_string(USER_HTML, models=models, winners=winners)

@app.route('/buy/<cat>', methods=['POST'])
def buy(cat):
    t_num = random.randint(100000, 999999)
    new_t = Ticket(user_name=request.form['name'], phone_number=request.form['phone'], 
                   address=request.form['address'], category=cat, ticket_number=t_num)
    db.session.add(new_t)
    db.session.commit()
    flash(f"Ticket Booked! No: {t_num}")
    return redirect('/')

# --- Admin Routes ---
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if request.form.get('password') == 'admin123': # CHANGE THIS PASSWORD
            session['logged_in'] = True
            return redirect('/admin')
    
    if not session.get('logged_in'):
        return '<div class="container mt-5 text-center"><form method="POST">Password: <input name="password" type="password"><button class="btn btn-dark ms-2">Login</button></form></div>'
    
    tickets = Ticket.query.all()
    models = MobileConfig.query.all()
    return render_template_string(ADMIN_HTML, tickets=tickets, models=models)

@app.route('/admin/update/<cat>', methods=['POST'])
def update_mobile(cat):
    if not session.get('logged_in'): return redirect('/admin')
    m = MobileConfig.query.filter_by(category_key=cat).first()
    m.model_name = request.form['model']
    m.specs = request.form['specs']
    m.price = request.form['price']
    db.session.commit()
    return redirect('/admin')

@app.route('/admin/draw')
def run_draw():
    if not session.get('logged_in'): return redirect('/admin')
    tickets = Ticket.query.all()
    if tickets:
        winner = random.choice(tickets)
        new_w = Winner(user_name=winner.user_name, category=winner.category, ticket_number=winner.ticket_number)
        db.session.add(new_w)
        Ticket.query.delete() # Clear all tickets after draw
        db.session.commit()
    return redirect('/admin')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect('/')

if __name__ == '__main__':
    init_data()
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
