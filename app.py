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
app.config['SECRET_KEY'] = 'smart-win-v5-fixed'

db = SQLAlchemy(app)

# --- Database Models ---
class MobileConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_key = db.Column(db.String(50), unique=True)
    model_name = db.Column(db.String(100))
    specs = db.Column(db.String(255))
    price = db.Column(db.Integer)
    color = db.Column(db.String(20))

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

# --- UI Designs ---
NAVBAR = """<nav class="navbar navbar-dark bg-dark shadow-sm mb-4"><div class="container"><a class="navbar-brand fw-bold" href="/">📱 SMART-WIN</a><a class="btn btn-outline-info btn-sm" href="/admin">Admin Panel</a></div></nav>"""

USER_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Smart-Win Mobile Lottery</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://jsdelivr.net">
    <style>
        body { background: #0b0e14; color: white; font-family: 'Segoe UI', sans-serif; }
        .card-lottery { background: #161b22; border: 1px solid #30363d; border-radius: 20px; position: relative; margin-bottom: 25px; transition: 0.3s; }
        .card-lottery:hover { transform: translateY(-10px); }
        .price-badge { position: absolute; top: -15px; right: 15px; background: #238636; padding: 5px 15px; border-radius: 10px; font-weight: bold; }
    </style>
</head>
<body>
    """ + NAVBAR + """
    <div class="container text-center mb-5">
        <h1 class="fw-bold">Premium Mobile Lottery</h1>
        <p class="text-muted">Enter now to win the latest smartphones daily at 8 PM.</p>
    </div>
    <div class="container">
        {% with messages = get_flashed_messages() %}{% if messages %}{% for m in messages %}<div class="alert alert-success text-center shadow">{{m}}</div>{% endfor %}{% endif %}{% endwith %}
        <div class="row">
            {% for m in models %}
            <div class="col-md-4">
                <div class="card card-lottery p-4 h-100 shadow">
                    <div class="price-badge">₹{{ m.price }}</div>
                    <h3 style="color: {{m.color}}">{{ m.model_name }}</h3>
                    <p class="small text-muted">{{ m.specs }}</p>
                    <hr class="border-secondary">
                    <form action="/buy/{{ m.category_key }}" method="POST" class="mt-auto">
                        <input name="name" placeholder="Full Name" class="form-control bg-dark text-white mb-2" required>
                        <input name="phone" placeholder="WhatsApp Number" class="form-control bg-dark text-white mb-2" required>
                        <textarea name="address" placeholder="Delivery Address" class="form-control bg-dark text-white mb-3" required></textarea>
                        <button class="btn w-100 fw-bold text-white shadow-sm" style="background: {{m.color}}">GET TICKET</button>
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
<body class="bg-light">
    <div class="container mt-5">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2>Admin Dashboard</h2>
            <a href="/logout" class="btn btn-danger btn-sm">Logout</a>
        </div>
        <div class="row">
            <div class="col-md-8">
                <div class="card p-3 shadow-sm mb-4">
                    <h4>Active Tickets (Today)</h4>
                    <table class="table table-striped mt-2">
                        <thead><tr><th>Name</th><th>Phone</th><th>Category</th><th>Ticket</th></tr></thead>
                        <tbody>
                            {% for t in tickets %}
                            <tr><td>{{t.user_name}}</td><td>{{t.phone_number}}</td><td>{{t.category}}</td><td>#{{t.ticket_number}}</td></tr>
                            {% else %}
                            <tr><td colspan="4" class="text-center">No tickets booked yet.</td></tr>
                            {% endfor %}
                        </tbody>
                    </table>
                    <a href="/admin/draw" class="btn btn-warning w-100 fw-bold mt-2" onclick="return confirm('Draw winners and CLEAR all tickets?')">RUN DRAW NOW</a>
                </div>
            </div>
            <div class="col-md-4">
                <h4>Update Mobile Info</h4>
                {% for m in models %}
                <form action="/admin/update/{{m.category_key}}" method="POST" class="card p-3 mb-3 shadow-sm border-0">
                    <label class="badge bg-secondary mb-2">{{ m.category_key }}</label>
                    <input name="model" value="{{m.model_name}}" class="form-control mb-2" placeholder="Model Name">
                    <input name="specs" value="{{m.specs}}" class="form-control mb-2" placeholder="Specs">
                    <input name="price" value="{{m.price}}" class="form-control mb-2" placeholder="Ticket Price">
                    <button class="btn btn-primary btn-sm w-100">Save Changes</button>
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
    return render_template_string(USER_HTML, models=models)

@app.route('/buy/<cat>', methods=['POST'])
def buy(cat):
    t_num = random.randint(100000, 999999)
    new_t = Ticket(user_name=request.form['name'], phone_number=request.form['phone'], address=request.form['address'], category=cat, ticket_number=t_num)
    db.session.add(new_t)
    db.session.commit()
    flash(f"Success! Your Ticket Number is #{t_num}")
    return redirect('/')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if request.form.get('password') == 'admin123': # CHANGE THIS
            session['logged_in'] = True
            return redirect('/admin')
    if not session.get('logged_in'):
        return '<div class="container mt-5 text-center shadow p-5 bg-light rounded"><form method="POST"><h3>Admin Login</h3><input name="password" type="password" class="form-control w-25 mx-auto my-3"><button class="btn btn-dark">Login</button></form></div>'
    tickets = Ticket.query.all()
    models = MobileConfig.query.all()
    return render_template_string(ADMIN_HTML, tickets=tickets, models=models)

@app.route('/admin/update/<cat>', methods=['POST'])
def update_mobile(cat):
    if not session.get('logged_in'): return redirect('/admin')
    m = MobileConfig.query.filter_by(category_key=cat).first()
    m.model_name = request.form['model']
    m.specs = request.form['specs']
    m.price = int(request.form['price'])
    db.session.commit()
    return redirect('/admin')

@app.route('/admin/draw')
def run_draw():
    if not session.get('logged_in'): return redirect('/admin')
    # Simple draw: 1 winner for each category that has tickets
    cats = ['low_cost', 'mid_range', 'flagship']
    for c in cats:
        tickets = Ticket.query.filter_by(category=c).all()
        if tickets:
            winner = random.choice(tickets)
            new_w = Winner(user_name=winner.user_name, category=c, ticket_number=winner.ticket_number)
            db.session.add(new_w)
    Ticket.query.delete() 
    db.session.commit()
    flash("Draw Successful! Winners picked and tickets cleared.")
    return redirect('/admin')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect('/')

# --- Fixed Startup ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Seed initial data if missing
        if not MobileConfig.query.first():
            configs = [
                MobileConfig(category_key='low_cost', model_name='Redmi 13C', specs='5000mAh, 50MP', price=50, color='#21d4fd'),
                MobileConfig(category_key='mid_range', model_name='OnePlus Nord', specs='100W, AMOLED', price=150, color='#b721ff'),
                MobileConfig(category_key='flagship', model_name='iPhone 15', specs='Titanium, 4K Video', price=500, color='#ff4b2b')
            ]
            db.session.bulk_save_objects(configs)
            db.session.commit()
    
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
