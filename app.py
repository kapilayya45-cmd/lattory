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
app.config['SECRET_KEY'] = 'ultra-stylish-split-view-2024'

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

# --- Ultra Stylish Split UI ---
USER_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>SMART-WIN | Professional Split View</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://jsdelivr.net">
    <link rel="stylesheet" href="https://cloudflare.com">
    <style>
        @import url('https://googleapis.com');
        body { background: #050505; color: #fff; font-family: 'Inter', sans-serif; }
        .hero { padding: 40px 0; text-align: center; border-bottom: 1px solid #222; }
        .hero h1 { font-family: 'Syncopate', sans-serif; font-size: 2rem; color: #00f2ff; text-shadow: 0 0 10px #00f2ff; }
        
        .timer-box { background: rgba(255,255,255,0.03); border: 1px solid #00f2ff; padding: 10px 20px; border-radius: 50px; display: inline-block; margin-top: 10px; }
        #countdown { font-size: 1.5rem; font-weight: 800; color: #fff; }

        /* SPLIT CARD DESIGN */
        .card-split { 
            background: #111; 
            border: 1px solid #222; 
            border-radius: 30px; 
            overflow: hidden; 
            margin-bottom: 40px; 
            transition: 0.3s;
            display: flex;
            flex-wrap: wrap;
        }
        .card-split:hover { border-color: #00f2ff; box-shadow: 0 0 30px rgba(0,242,255,0.1); }
        
        .img-side { 
            flex: 1; 
            min-width: 300px; 
            background: #fff; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            padding: 20px;
            position: relative;
        }
        .mobile-img { max-width: 100%; max-height: 350px; object-fit: contain; }
        
        .detail-side { 
            flex: 1.2; 
            min-width: 300px; 
            padding: 40px; 
            display: flex; 
            flex-direction: column; 
            justify-content: center;
        }
        
        .price-badge { background: #00f2ff; color: #000; padding: 8px 25px; border-radius: 50px; font-weight: 800; font-size: 1.4rem; display: inline-block; margin-bottom: 20px; width: fit-content; }
        .spec-text { color: #888; font-size: 1rem; line-height: 1.6; border-left: 3px solid #00f2ff; padding-left: 15px; margin-bottom: 25px; }

        .form-control { background: #1a1a1a; border: 1px solid #333; color: #fff; border-radius: 12px; margin-bottom: 10px; padding: 12px; }
        .form-control:focus { background: #222; border-color: #00f2ff; color: #fff; box-shadow: none; }
        
        .btn-buy { background: #fff; color: #000; font-weight: 800; border-radius: 12px; padding: 15px; border: none; width: 100%; text-transform: uppercase; letter-spacing: 1px; }
        .btn-buy:hover { background: #00f2ff; box-shadow: 0 0 20px #00f2ff; }

        @media (max-width: 768px) {
            .card-split { flex-direction: column; }
            .img-side { height: 250px; }
        }
        
        .whatsapp-float { position: fixed; bottom: 30px; right: 30px; background: #25d366; width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 30px; color: white; text-decoration: none; z-index: 1000; }
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
            <div class="alert alert-info bg-dark border-info text-info text-center rounded-pill mb-4">{{m}}</div>
        {% endfor %}{% endif %}{% endwith %}

        {% for m in models %}
        <div class="card-split shadow-lg">
            <!-- LEFT SIDE: IMAGE -->
            <div class="img-side">
                <img src="{{ m.image_url }}" onerror="this.src='https://placeholder.com{{m.model_name}}'" class="mobile-img">
            </div>
            
            <!-- RIGHT SIDE: DETAILS & FORM -->
            <div class="detail-side">
                <div class="price-badge">₹{{ m.price }} ONLY</div>
                <h2 class="fw-bold mb-2" style="color: {{m.color}}">{{ m.model_name }}</h2>
                <p class="spec-text">{{ m.specs }}</p>
                
                <form action="/buy/{{ m.category_key }}" method="POST">
                    <div class="row">
                        <div class="col-md-6">
                            <input name="name" placeholder="Enter Full Name" class="form-control" required>
                        </div>
                        <div class="col-md-6">
                            <input name="phone" placeholder="WhatsApp Number" class="form-control" required>
                        </div>
                    </div>
                    <textarea name="address" placeholder="Complete Shipping Address" class="form-control" rows="2" required></textarea>
                    <button class="btn-buy mt-2">BOOK MY TICKET NOW</button>
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

# --- Routes & Logic (Same as before but simplified) ---
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
    flash(f"🎉 TICKET # {t_num} BOOKED FOR {request.form['name']}!")
    return redirect('/')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST' and request.form.get('password') == 'admin123':
        session['logged_in'] = True
        return redirect('/admin')
    if not session.get('logged_in'):
        return '<body style="background:#000;color:#fff;text-align:center;padding:50px;"><form method="POST">ADMIN KEY: <input name="password" type="password"><button>LOGIN</button></form></body>'
    tickets = Ticket.query.all()
    models = MobileConfig.query.all()
    return render_template_string(ADMIN_UI, tickets=tickets, models=models)

ADMIN_UI = """
<!DOCTYPE html><html><head><link rel="stylesheet" href="https://jsdelivr.net"></head>
<body class="bg-dark text-white p-4"><div class="container">
    <h3>Admin Panel <a href="/logout" class="btn btn-danger btn-sm float-end">Logout</a></h3><hr>
    <div class="row">
        <div class="col-md-7">
            <h4>Live Bookings</h4>
            <table class="table table-dark"><tbody>{% for t in tickets %}<tr><td>{{t.user_name}}</td><td>{{t.phone_number}}</td><td>#{{t.ticket_number}}</td></tr>{% endfor %}</tbody></table>
            <a href="/admin/draw" class="btn btn-info w-100">RUN DRAW</a>
        </div>
        <div class="col-md-5">
            <h4>Update Catalog</h4>
            {% for m in models %}
            <form action="/admin/update/{{m.category_key}}" method="POST" class="card bg-secondary p-2 mb-2 border-0">
                <input name="model" value="{{m.model_name}}" class="form-control mb-1">
                <input name="specs" value="{{m.specs}}" class="form-control mb-1">
                <input name="price" value="{{m.price}}" class="form-control mb-1">
                <input name="image" value="{{m.image_url}}" class="form-control mb-1">
                <button class="btn btn-dark btn-sm w-100">Save</button>
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

# --- Database Startup ---
with app.app_context():
    db.create_all()
    if not MobileConfig.query.first():
        configs = [
            MobileConfig(category_key='low_cost', model_name='Redmi 13C', specs='5000mAh Battery | 50MP AI Camera | 8GB RAM', price=50, color='#00f2ff', image_url='https://media-amazon.com'),
            MobileConfig(category_key='mid_range', model_name='OnePlus Nord CE 4', specs='100W SuperVOOC | AMOLED Display | Sony Sensor', price=150, color='#b721ff', image_url='https://media-amazon.com'),
            MobileConfig(category_key='flagship', model_name='iPhone 15 Pro', specs='Titanium Build | A17 Pro Chip | 48MP Pro Camera', price=500, color='#ff4b2b', image_url='https://media-amazon.com')
        ]
        db.session.bulk_save_objects(configs)
        db.session.commit()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
