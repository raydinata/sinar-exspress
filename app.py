import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from fsm import ChatbotFSM

app = Flask(__name__)
CORS(app)

fsm_bot = ChatbotFSM()

# Route untuk menampilkan index.html saat orang membuka web
@app.route('/')
def home():
    return render_template('index.html')

# Route API untuk Chatbot
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    current_state = data.get('state', 'GREETING')

    reply, next_state = fsm_bot.process(user_message, current_state)

    return jsonify({
        'reply': reply,
        'next_state': next_state
    })

if __name__ == '__main__':
    # Konfigurasi untuk hosting Render
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)