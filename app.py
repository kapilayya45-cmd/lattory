from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_apscheduler import APScheduler
import random
import os
from datetime import datetime

app = Flask(__name__)

# --- Database & Config ---
basedir = os.path.abspath(os.path.dirname(__file__))
# Database file path simplified for Railway
db_path = os.path.join(basedir, 'lottery.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'mobile_lottery_secure_key_99'

db = SQLAlchemy(app)
scheduler = APScheduler()

# --- Database Models ---
class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    address = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
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

# --- Draw Logic (8 PM Daily) ---
def run_lottery_draw():
    with app.app_context():
        for cat_key, info in CATEGORIES.items():
            tickets = Ticket.query.filter_by(category=cat_key).all()
            if tickets:
                winner_ticket = random.choice(tickets)
                new_winner = Winner(
                    user_name=winner_ticket.user_name,
                    category=info['name'],
                    ticket_number=winner_ticket.ticket_number
                )
                db.session.add(new_winner)
                Ticket.query.filter_by(category=cat_key).delete()
        db.session.commit()

# --- Routes ---
@app.route('/')
def index():
    winners = Winner.query.order_by(Winner.draw_date.desc()).all()
    return render_template('index.html', categories=CATEGORIES, winners=winners)

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
    
    flash(f"Success! Your Ticket Number is {t_num}")
    return redirect(url_for('index'))

# --- Startup Logic ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Database create chestundi
    
    # Scheduler start
    if not scheduler.running:
        scheduler.add_job(id='daily_draw', func=run_lottery_draw, trigger='cron', hour=20, minute=0)
        scheduler.start()
        
    app.run(debug=False) # Production lo debug False
