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
app.config['SECRET_KEY'] = 'ultra-stylish-lottery-2024'

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

# --- Ultra Stylish UI ---
USER_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SMART-WIN | Ultra Mobile Lottery</title>
    <link rel="stylesheet" href="https://jsdelivr.net">
    <link rel="stylesheet" href="https://cloudflare.com">
    <style>
        @import url('https://googleapis.com');

        :root { --bg: #050505; --card-bg: #111; --accent: #00f2ff; }
        
        body { background: var(--bg); color: #fff; font-family: 'Inter', sans-serif; overflow-x: hidden; }
        
        /* Neon Background Glows */
        .glow-bg { position: fixed; width: 300px; height: 300px; background: rgba(0, 242, 255, 0.15); filter: blur(120px); border-radius: 50%; z-index: -1; }

        .hero { padding: 80px 0 40px; text-align: center; }
        .hero h1 { font-family: 'Syncopate', sans-serif; font-weight: 700; font-size: 3rem; letter-spacing: 5px; text-transform: uppercase; background: linear-gradient(to right, #fff, var(--accent)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }

        /* Stylish Timer */
        .timer-container { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); display: inline-block; padding: 15px 40px; border-radius: 100px; backdrop-filter: blur(10px); box-shadow: 0 0 30px rgba(0, 242, 255, 0.1); margin-top: 20px; }
        #countdown { font-size: 1.8rem; font-weight: 700; color: var(--accent); text-shadow: 0 0 10px var(--accent); }

        /* Card Styling */
        .card-lottery { background: var(--card-bg); border: 1px solid rgba(255,255,255,0.05); border-radius: 30px; position: relative; transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); overflow: hidden; margin-bottom: 30px; }
        .card-lottery:hover { transform: scale(1.05); border-color: var(--accent); box-shadow: 0 0 40px rgba(0, 242, 255, 0.2); }
        .price-tag { position: absolute; top: 20px; right: 20px; background: var(--accent); color: #000; padding: 5px 20px; border-radius: 50px; font-weight: 800; font-size: 1.2rem; box-shadow: 0 0 15px var(--accent); }
        .mobile-img { width: 100%; height: 220px; object-fit: contain; padding: 20px; filter: drop-shadow(0 0 15px rgba(255,255,255,0.1)); }

        .form-control { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); color: #fff; border-radius: 15px; padding: 12px; }
        .form-control:focus { background: rgba(255,255,255,0.1); color: #fff; border-color: var(--accent); box-shadow: none; }
        .btn-join { background: #fff; color: #000; font-weight: 800; border-radius: 15px; padding: 15px; border: none; text-transform: uppercase; transition: 0.3s; }
        .btn-join:hover { background: var(--accent); letter-spacing: 2px; }

        /* Hall of Fame */
        .winner-section { background: rgba(255,255,255,0.02); border: 1px dashed rgba(255,255,255,0.1); border-radius: 30px; padding: 40px; margin-bottom: 50px; }
        
        .whatsapp-btn { position: fixed; bottom: 30px; right: 30px; width: 65px; height: 65px; background: #25d366; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 35px; color: #fff; text-decoration: none; z-index: 1000; box-shadow: 0 0 20px rgba(37, 211, 102, 0.4); }
    </style>
</head>
<body>
    <div class="glow-bg" style="top: 10%; left: 10%;"></div>
    <div class="glow-bg" style="bottom: 10%; right: 10%; background: rgba(242, 17, 112, 0.1);"></div>

    <nav class="navbar navbar-dark py-4">
        <div class="container justify-content-center">
            <a class="navbar-brand fw-bold" href="/" style="letter-spacing: 3px; font-family: 'Syncopate';">SMART-WIN</a>
            <a href="/admin" class="ms-4 text-secondary text-decoration-none small">ADMIN</a>
        </div>
    </nav>

    <div class="hero">
        <div class="container">
            <h1>The Ultimate Draw</h1>
            <p class="text-secondary mt-3">Premium devices. Unbelievable odds.</p>
            <div class="timer-container">
                <div id="countdown">00:00:00:00</div>
            </div>
        </div>
    </div>

    <div class="container">
        {% with messages = get_flashed_messages() %}{% if messages %}{% for m in messages %}
            <div class="alert alert-info bg-transparent border-info text-info text-center rounded-pill">{{m}}</div>
        {% endfor %}{% endif %}{% endwith %}

        {% if winners %}
        <div class="winner-section">
            <h3 class="text-center mb-4" style="letter-spacing: 5px; font-family: 'Syncopate'; font-size: 1.2rem; color: #ffc107;">HALL OF FAME</h3>
            <div class="table-responsive">
                <table class="table table-dark border-0">
                    <tbody class="text-center">
                        {% for w in winners %}
                        <tr class="align-middle">
                            <td class="text-secondary small">{{ w.draw_date.strftime('%d %b') }}</td>
                            <td class="fw-bold">{{ w.user_name }}</td>
                            <td><span class="badge rounded-pill px-3 py-2" style="background: rgba(255,255,255,0.1);">{{ w.category }}</span></td>
                            <td class="text-info fw-bold">#{{ w.ticket_number }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
        {% endif %}

        <div class="row">
            {% for m in models %}
            <div class="col-lg-4 col-md-6">
                <div class="card-lottery shadow-lg">
                    <div class="price-tag">₹{{ m.price }}</div>
                    <img src="{{ m.image_url }}" class="mobile-img">
                    <div class="p-4 pt-0">
                        <h3 class="fw-bold mb-1" style="color: {{m.color}}">{{ m.model_name }}</h3>
                        <p class="text-secondary small mb-4">{{ m.specs }}</p>
                        <form action="/buy/{{ m.category_key }}" method="POST">
                            <input name="name" placeholder="YOUR NAME" class="form-control mb-2" required>
                            <input name="phone" placeholder="WHATSAPP NUMBER" class="form-control mb-2" required>
                            <textarea name="address" placeholder="SHIPPING ADDRESS" class="form-control mb-4" rows="2" required></textarea>
                            <button class="btn-join w-100">BOOK NOW</button>
                        </form>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>

    <a href="https://wa.me" class="whatsapp-btn" target="_blank"><i class="fab fa-whatsapp"></i></a>

    <script>
        function updateTimer() {
            const now = new Date();
            const draw = new Date();
            draw.setHours(20, 0, 0, 0);
            if (now > draw) draw.setDate(draw.getDate() + 1);
            const diff = draw - now;
            const h = String(Math.floor(diff / 3600000)).padStart(2, '0');
            const m = String(Math.floor((diff % 3600000) / 60000)).padStart(2, '0');
            const s = String(Math.floor((diff % 60000) / 1000)).padStart(2, '0');
            document.getElementById('countdown').innerHTML = `${h}:${m}:${s}`;
        }
        setInterval(updateTimer, 1000);
        updateTimer();
    </script>
</body>
</html>
"""

# --- Routes & Logic ---
@app.route('/')
def index():
    models = MobileConfig.query.all()
    winners = Winner.query.order_by(Winner.draw_date.desc()).limit(5).all()
    return render_template_string(USER_HTML, models=models, winners=winners)

@app.route('/buy/<cat>', methods=['POST'])
def buy(cat):
    t_num = random.randint(100000, 999999)
    new_t = Ticket(user_name=request.form['name'], phone_number=request.form['phone'], address=request.form['address'], category=cat, ticket_number=t_num)
    db.session.add(new_t)
    db.session.commit()
    flash(f"TICKET # {t_num} RESERVED SUCCESSFULLY")
    return redirect('/')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if request.form.get('password') == 'admin123':
            session['logged_in'] = True
            return redirect('/admin')
    if not session.get('logged_in'):
        return render_template_string('<body style="background:#000;color:#fff;text-align:center;padding:100px;"><form method="POST">ADMIN KEY: <input name="password" type="password" style="background:#222;color:#fff;border:1px solid #444;padding:10px;"><button style="padding:10px 20px;background:#00f2ff;border:none;margin-left:10px;">ENTER</button></form></body>')
    
    tickets = Ticket.query.all()
    models = MobileConfig.query.all()
    return render_template_string(ADMIN_UI, tickets=tickets, models=models)

ADMIN_UI = """
<!DOCTYPE html>
<html>
<head><title>ADMIN | SMART-WIN</title><link rel="stylesheet" href="https://jsdelivr.net"></head>
<body class="bg-dark text-white p-5">
    <div class="container">
        <h2>DASHBOARD <a href="/logout" class="btn btn-danger btn-sm float-end">LOGOUT</a></h2>
        <hr border-white>
        <div class="row">
            <div class="col-md-8">
                <h4>LIVE TICKETS</h4>
                <table class="table table-dark table-striped">
                    <thead><tr><th>NAME</th><th>PHONE</th><th>CAT</th><th>TICKET</th></tr></thead>
                    <tbody>{% for t in tickets %}<tr><td>{{t.user_name}}</td><td>{{t.phone_number}}</td><td>{{t.category}}</td><td>#{{t.ticket_number}}</td></tr>{% endfor %}</tbody>
                </table>
                <a href="/admin/draw" class="btn btn-info w-100 fw-bold">EXECUTE DRAW (PICK WINNER)</a>
            </div>
            <div class="col-md-4">
                <h4>CATALOG</h4>
                {% for m in models %}
                <form action="/admin/update/{{m.category_key}}" method="POST" class="card bg-secondary p-3 mb-2">
                    <input name="model" value="{{m.model_name}}" class="form-control mb-1">
                    <input name="specs" value="{{m.specs}}" class="form-control mb-1">
                    <input name="price" value="{{m.price}}" class="form-control mb-1">
                    <input name="image" value="{{m.image_url}}" class="form-control mb-1">
                    <button class="btn btn-dark btn-sm">UPDATE {{m.category_key}}</button>
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
    tickets = Ticket.query.all()
    if tickets:
        winner = random.choice(tickets)
        new_w = Winner(user_name=winner.user_name, category=winner.category, ticket_number=winner.ticket_number)
        db.session.add(new_w)
        Ticket.query.delete()
        db.session.commit()
    return redirect('/admin')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect('/')

# --- Database Initialize ---
with app.app_context():
    db.create_all()
    if not MobileConfig.query.first():
        configs = [
            MobileConfig(category_key='low_cost', model_name='Redmi 13C', specs='5000mAh, 50MP AI', price=50, color='#00f2ff', image_url='https://media-amazon.com'),
            MobileConfig(category_key='mid_range', model_name='OnePlus Nord CE 4', specs='100W SuperVOOC', price=150, color='#9d50bb', image_url='https://media-amazon.com'),
            MobileConfig(category_key='flagship', model_name='iPhone 15 Pro', specs='A17 Pro Titanium', price=500, color='#f21170', image_url='https://media-amazon.com')
        ]
        db.session.bulk_save_objects(configs)
        db.session.commit()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
