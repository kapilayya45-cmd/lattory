import os
import random
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_apscheduler import APScheduler

app = Flask(__name__)

# --- Railway Configuration ---
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'lottery.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'lottery_secret_key_2024'

db = SQLAlchemy(app)
scheduler = APScheduler()

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

# --- Draw Logic ---
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
    try:
        winners = Winner.query.order_by(Winner.draw_date.desc()).all()
    except:
        winners = []
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

# --- App Init & Scheduler ---
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    if not scheduler.running:
        scheduler.add_job(id='daily_draw', func=run_lottery_draw, trigger='cron', hour=20, minute=0)
        scheduler.start()
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
