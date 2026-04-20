import os
import random
from flask import Flask, request, redirect, flash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret123'

# --- Simple Design (No HTML File Required) ---
def get_html(message=""):
    return f"""
    <html>
    <head><title>Mobile Lottery</title><meta name='viewport' content='width=device-width, initial-scale=1.0'><link rel='stylesheet' href='https://jsdelivr.net'></head>
    <body class='bg-light'><div class='container mt-5 text-center'>
        <div class='bg-primary text-white p-4 rounded shadow mb-4'><h1>📱 Daily Mobile Lottery</h1><p>Next Draw: 8:00 PM</p></div>
        <div class='alert alert-info'>{message if message else 'Welcome! Buy your ticket below.'}</div>
        <div class='row'>
            <div class='col-md-4 mb-3'><div class='card p-3 shadow'><h4>Budget (Below 10k)</h4><p class='text-success fw-bold'>₹50</p><form method='POST' action='/buy/low'><input name='name' placeholder='Name' class='form-control mb-2' required><button class='btn btn-primary w-100'>Buy Ticket</button></form></div></div>
            <div class='col-md-4 mb-3'><div class='card p-3 shadow'><h4>Mid-Range (Above 10k)</h4><p class='text-success fw-bold'>₹150</p><form method='POST' action='/buy/mid'><input name='name' placeholder='Name' class='form-control mb-2' required><button class='btn btn-primary w-100'>Buy Ticket</button></form></div></div>
            <div class='col-md-4 mb-3'><div class='card p-3 shadow'><h4>Flagship (High Cost)</h4><p class='text-success fw-bold'>₹500</p><form method='POST' action='/buy/high'><input name='name' placeholder='Name' class='form-control mb-2' required><button class='btn btn-primary w-100'>Buy Ticket</button></form></div></div>
        </div>
    </div></body></html>
    """

@app.route('/')
def index():
    return get_html()

@app.route('/buy/<cat>', methods=['POST'])
def buy(cat):
    name = request.form.get('name')
    t_num = random.randint(100000, 999999)
    return get_html(f"Ticket Booked for {name}! Number: {t_num}")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
