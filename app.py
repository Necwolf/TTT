from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello from Flask on Fly!"

@app.route('/tally-webhook', methods=['POST'])
def tally_webhook():
    data = request.json
    print("Tally webhook received:", data)
    return jsonify({"status": "ok"}), 200