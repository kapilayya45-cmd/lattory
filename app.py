import os
import random
from datetime import datetime
from flask import Flask, request, redirect, url_for, flash, render_template_string, session, jsonify
from flask_sqlalchemy import SQLAlchemy
import google.generativeai as genai

app = Flask(__name__)

# --- Configuration ---
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'lottery.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'gemini-ai-ultra-split-view'

# --- Gemini AI Setup ---
# Replace 'YOUR_GEMINI_API_KEY' with your actual key
genai.configure(api_key="YOUR_GEMINI_API_KEY")
model_ai = genai.GenerativeModel('gemini-pro')

db = SQLAlchemy(app)

# --- Database Models (Same as before) ---
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

# --- HTML Design (Split View + AI Chatbot) ---
USER_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>SMART-WIN | Gemini AI Powered</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://jsdelivr.net">
    <link rel="stylesheet" href="https://cloudflare.com">
    <style>
        @import url('https://googleapis.com');
        body { background: #050505; color: #fff; font-family: 'Space Grotesk', sans-serif; }
        .hero { padding: 40px 0; text-align: center; border-bottom: 1px solid #222; }
        .hero h1 { font-family: 'Syncopate', sans-serif; font-size: 2rem; color: #00f2ff; text-shadow: 0 0 10px #00f2ff; }
        .timer-wrap { background: rgba(255,255,255,0.03); border: 1px solid #00f2ff; padding: 10px 20px; border-radius: 50px; display: inline-block; }
        
        .split-card { background: #111; border: 1px solid #222; border-radius: 40px; margin-bottom: 50px; display: flex; flex-direction: row-reverse; overflow: hidden; transition: 0.4s; }
        .img-side { flex: 1; background: #fff; display: flex; align-items: center; justify-content: center; padding: 30px; }
        .mobile-img { max-width: 100%; max-height: 400px; object-fit: contain; }
        .detail-side { flex: 1.2; padding: 50px; display: flex; flex-direction: column; justify-content: center; }

        /* AI Chatbot Button */
        .ai-chat-btn { position: fixed; bottom: 30px; left: 30px; width: 65px; height: 65px; background: #6f42c1; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 30px; color: white; cursor: pointer; z-index: 1000; box-shadow: 0 0 20px rgba(111, 66, 193, 0.5); }
        #ai-chat-window { position: fixed; bottom: 110px; left: 30px; width: 300px; height: 400px; background: #111; border: 1px solid #333; border-radius: 20px; display: none; flex-direction: column; z-index: 1000; overflow: hidden; }
        #chat-content { flex: 1; padding: 15px; overflow-y: auto; font-size: 0.9rem; }
        .chat-input { padding: 10px; background: #222; border-top: 1px solid #333; display: flex; }
        .chat-input input { background: transparent; border: none; color: white; flex: 1; outline: none; }
        
        .btn-glow { background: #00f2ff; color: #000; font-weight: 800; border-radius: 15px; padding: 15px; border: none; text-transform: uppercase; letter-spacing: 2px; }
        @media (max-width: 992px) { .split-card { flex-direction: column; } .img-side { height: 300px; } }
    </style>
</head>
<body>
    <!-- Gemini AI Bot -->
    <div class="ai-chat-btn" onclick="toggleChat()"><i class="fas fa-robot"></i></div>
    <div id="ai-chat-window">
        <div class="bg-primary p-3 text-white fw-bold">Gemini AI Assistant</div>
        <div id="chat-content">Hi! Ask me about today's mobile lottery...</div>
        <div class="chat-input">
            <input type="text" id="ai-msg" placeholder="Ask AI...">
            <button onclick="askAI()" class="btn btn-sm btn-primary">Send</button>
        </div>
    </div>

    <div class="hero">
        <div class="container">
            <h1>SMART-WIN AI</h1>
            <div class="timer-wrap"><div id="countdown">00:00:00</div></div>
        </div>
    </div>

    <div class="container mt-5">
        {% for m in models %}
        <div class="split-card shadow-lg">
            <div class="img-side"><img src="{{ m.image_url }}" class="mobile-img"></div>
            <div class="detail-side">
                <div class="text-info fw-bold mb-2">ENTRY: ₹{{ m.price }}</div>
                <h2 style="color: {{m.color}}">{{ m.model_name }}</h2>
                <p class="text-secondary small mb-4">{{ m.specs }}</p>
                <form action="/buy/{{ m.category_key }}" method="POST">
                    <input name="name" placeholder="FULL NAME" class="form-control bg-dark text-white mb-2 border-secondary" required>
                    <input name="phone" placeholder="WHATSAPP NUMBER" class="form-control bg-dark text-white mb-2 border-secondary" required>
                    <textarea name="address" placeholder="DELIVERY ADDRESS" class="form-control bg-dark text-white mb-3 border-secondary" rows="2" required></textarea>
                    <button class="btn-glow w-100">BOOK TICKET</button>
                </form>
            </div>
        </div>
        {% endfor %}
    </div>

    <script>
        function toggleChat() { 
            const win = document.getElementById('ai-chat-window');
            win.style.display = win.style.display === 'flex' ? 'none' : 'flex';
        }

        async function askAI() {
            const msg = document.getElementById('ai-msg').value;
            const content = document.getElementById('chat-content');
            content.innerHTML += `<div class="text-info mt-2">You: ${msg}</div>`;
            document.getElementById('ai-msg').value = '';
            
            const response = await fetch('/ask-ai', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({prompt: msg})
            });
            const data = await response.json();
            content.innerHTML += `<div class="text-white mt-2">AI: ${data.answer}</div>`;
            content.scrollTop = content.scrollHeight;
        }

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

# --- AI Route ---
@app.route('/ask-ai', methods=['POST'])
def ask_ai():
    data = request.json
    prompt = data.get('prompt')
    try:
        response = model_ai.generate_content(f"Answer this query about a mobile lottery business in Telugu: {prompt}")
        return jsonify({"answer": response.text})
    except:
        return jsonify({"answer": "AI is busy, please try later!"})

@app.route('/')
def index():
    models = MobileConfig.query.all()
    return render_template_string(USER_HTML, models=models)

# ... (Insert Buy, Admin, Update routes from previous code here) ...

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
