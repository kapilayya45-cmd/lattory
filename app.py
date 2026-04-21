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
app.config['SECRET_KEY'] = 'ultra-timer-pro-9121'

db = SQLAlchemy(app)

# --- Database Models ---
class MobileConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_key = db.Column(db.String(50), unique=True)
    model_name = db.Column(db.String(100))
    specs = db.Column(db.String(255))
    price = db.Column(db.Integer)
    color = db.Column(db.String(20))
    image_url = db.Column(db.String(500))

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
USER_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>SMART-WIN | Ultra Modern Lottery</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://jsdelivr.net">
    <link rel="stylesheet" href="https://cloudflare.com">
    <style>
        @import url('https://googleapis.com');
        body { background: #050505; color: #fff; font-family: 'Inter', sans-serif; overflow-x: hidden; }
        .hero { padding: 60px 0; text-align: center; background: radial-gradient(circle at top, #111 0%, #050505 100%); }
        .hero h1 { font-family: 'Syncopate', sans-serif; font-size: 2.5rem; letter-spacing: 5px; color: #00f2ff; text-shadow: 0 0 20px #00f2ff; }
        
        /* THE TIMER */
        .timer-box { 
            background: rgba(255,255,255,0.05); 
            border: 1px solid #00f2ff; 
            padding: 15px 30px; 
            border-radius: 50px; 
            display: inline-block; 
            margin-top: 25px; 
            box-shadow: 0 0 15px rgba(0,242,255,0.2);
        }
        #countdown { font-size: 1.8rem; font-weight: 800; color: #fff; letter-spacing: 2px; }
        .timer-label { font-size: 0.7rem; color: #00f2ff; text-transform: uppercase; letter-spacing: 2px; }

        .card-lottery { background: #111; border: 1px solid #222; border-radius: 25px; transition: 0.4s; overflow: hidden; margin-bottom: 30px; position: relative; }
        .card-lottery:hover { transform: translateY(-10px); border-color: #00f2ff; box-shadow: 0 10px 30px rgba(0,242,255,0.1); }
        .price-badge { position: absolute; top: 15px; right: 15px; background: #00f2ff; color: #000; padding: 5px 15px; border-radius: 50px; font-weight: 800; z-index: 10; }
        .mobile-img { width: 100%; height: 200px; object-fit: contain; padding: 20px; }
        .btn-buy { background: #fff; color: #000; font-weight: 800; border-radius: 12px; padding: 12px; border: none; width: 100%; }
        .btn-buy:hover { background: #00f2ff; box-shadow: 0 0 20px #00f2ff; }
        .whatsapp-float { position: fixed; bottom: 30px; right: 30px; background: #25d366; width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 30px; color: white; text-decoration: none; z-index: 1000; box-shadow: 0 0 20px rgba(37,211,102,0.4); }
    </style>
</head>
<body>
    <a href="https://wa.me" class="whatsapp-float" target="_blank"><i class="fab fa-whatsapp"></i></a>

    <div class="hero">
        <div class="container">
            <h1>SMART-WIN</h1>
            <p class="text-secondary small mt-2">PREMIUM MOBILE LOTTERY SYSTEM</p>
            <div class="timer-box">
                <div class="timer-label">Next Draw Starts In</div>
                <div id="countdown">00:00:00</div>
            </div>
        </div>
    </div>

    <div class="container mt-5">
        {% with messages = get_flashed_messages() %}{% if messages %}{% for m in messages %}
            <div class="alert alert-info bg-dark border-info text-info text-center rounded-pill mb-4">{{m}}</div>
        {% endfor %}{% endif %}{% endwith %}

        <div class="row">
            {% for m in models %}
            <div class="col-md-4">
                <div class="card card-lottery">
                    <div class="price-badge">₹{{ m.price }}</div>
                    <img src="{{ m.image_url }}" class="mobile-img">
                    <div class="p-4 pt-0">
                        <h3 class="h5 fw-bold" style="color: {{m.color}}">{{ m.model_name }}</h3>
                        <p class="text-secondary small mb-3">{{ m.specs }}</p>
                        <form action="/buy/{{ m.category_key }}" method="POST">
                            <input name="name" placeholder="Name" class="form-control bg-dark border-secondary text-white mb-2" required>
                            <input name="phone" placeholder="WhatsApp" class="form-control bg-dark border-secondary text-white mb-2" required>
                            <textarea name="address" placeholder="Address" class="form-control bg-dark border-secondary text-white mb-3" rows="2" required></textarea>
                            <button class="btn-buy">BOOK TICKET</button>
                        </form>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>

    <script>
        function updateTimer() {
            const now = new Date();
            const draw = new Date();
            draw.setHours(20, 0, 0, 0); // 8:00 PM
            if (now > draw) draw.setDate(draw.getDate() + 1);
            
            const diff = draw - now;
            const h = String(Math.floor(diff / 3600000)).padStart(2, '0');
            const m = String(Math.floor((diff % 3600000) / 60000)).padStart(2, '0');
            const s = String(Math.floor((diff % 60000) / 1000)).padStart(2, '0');
            
            document.getElementById('countdown').innerHTML = h + ":" + m + ":" + s;
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
    models = MobileConfig.query.all()
    return render_template_string(USER_HTML, models=models)

@app.route('/buy/<cat>', methods=['POST'])
def buy(cat):
    t_num = random.randint(100000, 999999)
    new_t = Ticket(user_name=request.form['name'], phone_number=request.form['phone'], address=request.form['address'], category=cat, ticket_number=t_num)
    db.session.add(new_t)
    db.session.commit()
    flash(f"TICKET #{t_num} RESERVED!")
    return redirect('/')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if request.form.get('password') == 'admin123':
            session['logged_in'] = True
            return redirect('/admin')
    if not session.get('logged_in'):
        return '<body style="background:#000;color:#fff;text-align:center;padding:100px;"><form method="POST">ADMIN KEY: <input name="password" type="password"><button>LOGIN</button></form></body>'
    
    tickets = Ticket.query.all()
    models = MobileConfig.query.all()
    return render_template_string(ADMIN_UI, tickets=tickets, models=models)

ADMIN_UI = """
<!DOCTYPE html>
<html>
<head><title>Admin Dashboard</title><link rel="stylesheet" href="https://jsdelivr.net"></head>
<body class="bg-dark text-white p-5">
    <div class="container">
        <h2>DASHBOARD <a href="/logout" class="btn btn-danger btn-sm float-end">LOGOUT</a></h2>
        <hr border-white>
        <div class="row">
            <div class="col-md-8">
                <h4>ACTIVE TICKETS</h4>
                <table class="table table-dark">
                    <thead><tr><th>NAME</th><th>PHONE</th><th>CAT</th><th>NO</th></tr></thead>
                    <tbody>{% for t in tickets %}<tr><td>{{t.user_name}}</td><td>{{t.phone_number}}</td><td>{{t.category}}</td><td>#{{t.ticket_number}}</td></tr>{% endfor %}</tbody>
                </table>
                <a href="/admin/draw" class="btn btn-primary w-100">RUN DRAW</a>
            </div>
            <div class="col-md-4">
                <h4>MANAGE MODELS</h4>
                {% for m in models %}
                <form action="/admin/update/{{m.category_key}}" method="POST" class="card bg-secondary p-3 mb-2">
                    <input name="model" value="{{m.model_name}}" class="form-control mb-1">
                    <input name="specs" value="{{m.specs}}" class="form-control mb-1">
                    <input name="price" value="{{m.price}}" class="form-control mb-1">
                    <input name="image" value="{{m.image_url}}" class="form-control mb-1">
                    <button class="btn btn-dark btn-sm">UPDATE</button>
                </form>
                {% endfor %}
            </div>
        </div>
    </div>
</body>
</html>
"""

@app.route('/admin/update/<cat>', methods=['POST'])
def update_mobile(cat):
    if not session.get('logged_in'): return redirect('/admin')
    m = MobileConfig.query.filter_by(category_key=cat).first()
    m.model_name = request.form['model']
    m.specs = request.form['specs']
    m.price = int(request.form['price'])
    m.image_url = request.form['image']
    db.session.commit()
    return redirect('/admin')

@app.route('/admin/draw')
def run_draw():
    if not session.get('logged_in'): return redirect('/admin')
    # Simple logic
    Ticket.query.delete()
    db.session.commit()
    return redirect('/admin')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect('/')

# --- Database Startup ---
with app.app_context():
    db.create_all()
    if not MobileConfig.query.first():
        configs = [
            MobileConfig(category_key='low_cost', model_name='Redmi 13C', specs='Budget Powerhouse', price=50, color='#00f2ff', image_url='https://media-amazon.com'),
            MobileConfig(category_key='mid_range', model_name='OnePlus Nord CE 4', specs='100W SuperVOOC', price=150, color='#b721ff', image_url='https://media-amazon.com'),
            MobileConfig(category_key='flagship', model_name='iPhone 15 Pro', specs='Titanium Build', price=500, color='#ff4b2b', image_url='https://media-amazon.com')
        ]
        db.session.bulk_save_objects(configs)
        db.session.commit()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
