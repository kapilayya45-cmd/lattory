from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_apscheduler import APScheduler
import random
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lottery.db'
app.config['SECRET_KEY'] = 'secret_key_123'
db = SQLAlchemy(app)
scheduler = APScheduler()

# Database Models
class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    address = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False) # e.g., 'Below 10k'
    ticket_number = db.Column(db.Integer, unique=True)

class Winner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100))
    category = db.Column(db.String(50))
    ticket_number = db.Column(db.Integer)
    draw_date = db.Column(db.DateTime, default=datetime.utcnow)

# Categories and Pricing Info
CATEGORIES = {
    'below_10k': {'name': 'Budget Mobiles (Below 10k)', 'price': 50},
    'above_10k': {'name': 'Mid-Range Mobiles (Above 10k)', 'price': 150},
    'high_cost': {'name': 'Flagship Mobiles (iPhone/S24)', 'price': 500}
}

# 8 PM Draw Logic
def run_lottery_draw():
    with app.app_context():
        for cat_key in CATEGORIES.keys():
            tickets = Ticket.query.filter_by(category=cat_key).all()
            if tickets:
                winner_ticket = random.choice(tickets)
                new_winner = Winner(
                    user_name=winner_ticket.user_name,
                    category=CATEGORIES[cat_key]['name'],
                    ticket_number=winner_ticket.ticket_number
                )
                db.session.add(new_winner)
                # Clear old tickets for next day
                Ticket.query.filter_by(category=cat_key).delete()
        db.session.commit()
        print("8 PM Draw Completed Successfully!")

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
    
    flash(f"Ticket Booked! Your Number: {t_num} for {CATEGORIES[cat_key]['name']}")
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    # Schedule task for 8 PM (20:00)
    scheduler.add_job(id='DailyDraw', func=run_lottery_draw, trigger='cron', hour=20, minute=0)
    scheduler.start()
    app.run(debug=True)
