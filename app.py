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
app.config['SECRET_KEY'] = 'ultra-futuristic-split-9121'

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

# --- ULTRA STYLISH SPLIT UI (Left: Details, Right: Image) ---
USER_HTML = """
<!DOCTYPE html>
<html lang="te">
<head>
    <title>SMART-WIN | Futuristic Mobile Lottery</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://jsdelivr.net">
    <link rel="stylesheet" href="https://cloudflare.com">
    <style>
        @import url('https://googleapis.com');
        
        :root { --accent: #00f2ff; --bg: #050505; --card-bg: #111; }
        body { background: var(--bg); color: #fff; font-family: 'Space Grotesk', sans-serif; overflow-x: hidden; }
        
        /* Header & Hero */
        .hero { padding: 60px 0 40px; text-align: center; }
        .hero h1 { font-family: 'Syncopate', sans-serif; font-size: 2.5rem; letter-spacing: 8px; color: var(--accent); text-shadow: 0 0 20px rgba(0,242,255,0.5); }
        
        .timer-wrap { background: rgba(255,255,255,0.03); border: 1px solid var(--accent); padding: 10px 30px; border-radius: 50px; display: inline-block; margin-top: 20px; box-shadow: 0 0 15px rgba(0,242,255,0.2); }
        #countdown { font-size: 1.8rem; font-weight: 700; letter-spacing: 2px; }

        /* SPLIT VIEW CARD: LEFT(Details) - RIGHT(Image) */
        .split-card { 
            background: var(--card-bg); 
            border: 1px solid #222; 
            border-radius: 40px; 
            margin-bottom: 50px; 
            display: flex; 
            flex-direction: row-reverse; /* Force Right: Image, Left: Details */
            overflow: hidden; 
            transition: 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }
        .split-card:hover { border-color: var(--accent); transform: scale(1.02); box-shadow: 0 20px 40px rgba(0,0,0,0.5); }

        .img-side { 
            flex: 1; 
            background: #fff; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            padding: 30px;
        }
        .mobile-img { max-width: 100%; max-height: 400px; object-fit: contain; filter: drop-shadow(0 10px 20px rgba(0,0,0,0.2)); }

        .detail-side { 
            flex: 1.2; 
            padding: 50px; 
            display: flex; 
            flex-direction: column; 
            justify-content: center;
        }

        .price-tag { font-size: 1.2rem; color: var(--accent); font-weight: 700; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 10px; }
        .mobile-name { font-family: 'Syncopate', sans-serif; font-size: 1.8rem; margin-bottom: 15px; }
        .specs { color: #888; font-size: 0.95rem; margin-bottom: 30px; line-height: 1.8; border-left: 3px solid var(--accent); padding-left: 20px; }

        /* Modern Form */
        .form-control { background: #1a1a1a; border: 1px solid #333; color: #fff; border-radius: 15px; padding: 12px; margin-bottom: 15px; }
        .form-control:focus { background: #222; border-color: var(--accent); color: #fff; box-shadow: none; }
        .btn-glow { background: var(--accent); color: #000; font-weight: 800; border-radius: 15px; padding: 15px; border: none; text-transform: uppercase; letter-spacing: 2px; transition: 0.3s; }
        .btn-glow:hover { box-shadow: 0 0 30px var(--accent); transform: scale(1.05); }

        @media (max-width: 992px) {
            .split-card { flex-direction: column; } /* Stack on mobile */
            .img-side { height: 300px; }
        }

        .whatsapp-float { position: fixed; bottom: 30px; right: 30px; background: #25d366; width: 65px; height: 65px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 35px; color: white; text-decoration: none; z-index: 1000; box-shadow: 0 10px 20px rgba(0,0,0,0.3); }
    </style>
</head>
<body>
    <a href="https://wa.me" class="whatsapp-float shadow-lg" target="_blank"><i class="fab fa-whatsapp"></i></a>

    <div class="hero">
        <div class="container">
            <h1>SMART-WIN</h1>
            <div class="timer-wrap">
                <div id="countdown">00:00:00</div>
            </div>
        </div>
    </div>

    <div class="container mt-5">
        {% with messages = get_flashed_messages() %}{% if messages %}{% for m in messages %}
            <div class="alert alert-info bg-dark border-info text-info text-center rounded-pill mb-5">{{m}}</div>
        {% endfor %}{% endif %}{% endwith %}

        {% for m in models %}
        <div class="split-card shadow-lg">
            <!-- RIGHT SIDE: IMAGE -->
            <div class="img-side">
                <img src="{{ m.image_url }}" onerror="this.src='https://placeholder.com{{m.model_name}}'" class="mobile-img">
            </div>
            
            <!-- LEFT SIDE: DETAILS & FORM -->
            <div class="detail-side">
                <div class="price-tag">Entry Fee: ₹{{ m.price }}</div>
                <h2 class="mobile-name" style="color: {{m.color}}">{{ m.model_name }}</h2>
                <p class="specs">{{ m.specs }}</p>
                
                <form action="/buy/{{ m.category_key }}" method="POST">
                    <div class="row">
                        <div class="col-md-6"><input name="name" placeholder="FULL NAME" class="form-control" required></div>
                        <div class="col-md-6"><input name="phone" placeholder="WHATSAPP NUMBER" class="form-control" required></div>
                    </div>
                    <textarea name="address" placeholder="COMPLETE DELIVERY ADDRESS" class="form-control" rows="2" required></textarea>
                    <button class="btn-glow w-100">JOIN THE DRAW</button>
                </form>
            </div>
        </div>
        {% endfor %}
    </div>

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
            document.getElementById('countdown').innerHTML = h + ":" + m + ":" + s;
        }
        setInterval(updateTimer, 1000); updateTimer();
    </script>
</body>
</html>
"""

# --- Routes & Business Logic ---
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
    flash(f"🎉 TICKET # {t_num} CONFIRMED! GOOD LUCK.")
    return redirect('/')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST' and request.form.get('password') == 'admin123':
        session['logged_in'] = True
        return redirect('/admin')
    if not session.get('logged_in'):
        return '<body style="background:#000;color:#fff;text-align:center;padding:100px;"><form method="POST">ADMIN KEY: <input name="password" type="password" style="padding:10px;"><button style="padding:10px;">LOGIN</button></form></body>'
    tickets = Ticket.query.all()
    models = MobileConfig.query.all()
    return render_template_string(ADMIN_UI, tickets=tickets, models=models)

ADMIN_UI = """
<!DOCTYPE html><html><head><link rel="stylesheet" href="https://jsdelivr.net"></head>
<body class="bg-dark text-white p-5"><div class="container">
    <h3>ADMIN DASHBOARD <a href="/logout" class="btn btn-danger btn-sm float-end">LOGOUT</a></h3><hr>
    <div class="row">
        <div class="col-md-7">
            <h4>LIVE TICKETS</h4>
            <table class="table table-dark"><tbody>{% for t in tickets %}<tr><td>{{t.user_name}}</td><td>{{t.phone_number}}</td><td>#{{t.ticket_number}}</td></tr>{% endfor %}</tbody></table>
            <a href="/admin/draw" class="btn btn-primary w-100">EXECUTE DRAW</a>
        </div>
        <div class="col-md-5">
            <h4>MANAGE CATALOG</h4>
            {% for m in models %}
            <form action="/admin/update/{{m.category_key}}" method="POST" class="card bg-secondary p-3 mb-2 border-0">
                <input name="model" value="{{m.model_name}}" class="form-control mb-1">
                <input name="specs" value="{{m.specs}}" class="form-control mb-1">
                <input name="price" value="{{m.price}}" class="form-control mb-1">
                <input name="image" value="{{m.image_url}}" class="form-control mb-1">
                <button class="btn btn-dark btn-sm w-100">SAVE {{m.category_key}}</button>
            </form>
            {% endfor %}
        </div>
    </div></div></body></html>
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
            MobileConfig(category_key='low_cost', model_name='Redmi 13C', specs='5000mAh Battery | 50MP AI Triple Camera | Fast Display', price=50, color='#00f2ff', image_url='https://media-amazon.com'),
            MobileConfig(category_key='mid_range', model_name='OnePlus Nord CE 4', specs='100W SuperVOOC Charging | Sony Sensor | AMOLED 120Hz', price=150, color='#00f2ff', image_url='https://media-amazon.com'),
            MobileConfig(category_key='flagship', model_name='iPhone 15 Pro', specs='Titanium Grade Build | A17 Pro Gaming Chip | 48MP Pro Lens', price=500, color='#00f2ff', image_url='https://media-amazon.com')
        ]
        db.session.bulk_save_objects(configs)
        db.session.commit()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
