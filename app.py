import os
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import db
import threading
import time
import fetch_valetudo

# Load environment variables from .env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/heatmap', methods=['GET'])
def get_heatmap():
    conn = db.get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT x, y, value, timestamp FROM robot_data')
    rows = cur.fetchall()
    conn.close()
    heatmap = [dict(row) for row in rows]
    return jsonify({'heatmap': heatmap})

def background_fetcher():
    while True:
        fetch_valetudo.fetch_and_store()
        time.sleep(10)

if __name__ == '__main__':
    t = threading.Thread(target=background_fetcher, daemon=True)
    t.start()
    app.run(host=os.getenv('FLASK_HOST', '0.0.0.0'), port=int(os.getenv('FLASK_PORT', 5000)), debug=os.getenv('FLASK_DEBUG', 'False') == 'True')
