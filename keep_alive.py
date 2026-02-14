from flask import Flask
import threading

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is Running Stable"

def run():
    # রেন্ডারের জন্য পোর্ট ১০০০০ এ রান করা জরুরি
    app.run(host="0.0.0.0", port=10000)

def keep_alive():
    t = threading.Thread(target=run, daemon=True)
    t.start()
    
