import os
import requests
from dotenv import load_dotenv
import db

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

VALETUDO_HOST = os.getenv('VALETUDO_HOST')  # e.g. 192.168.1.123

# Construct the API URL for map/heatmap data
if VALETUDO_HOST:
    VALETUDO_API_URL = f'http://{VALETUDO_HOST}/api/map'
else:
    VALETUDO_API_URL = None

def fetch_and_store():
    if not VALETUDO_API_URL:
        print('VALETUDO_HOST not set in .env')
        return
    try:
        resp = requests.get(VALETUDO_API_URL, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        # Example: data['heatmap'] = [{"x":..., "y":..., "value":...}, ...]
        heatmap = data.get('heatmap', [])
        conn = db.get_db_connection()
        cur = conn.cursor()
        for point in heatmap:
            x = int(point['x'])
            y = int(point['y'])
            value = int(point['value'])
            cur.execute('INSERT INTO robot_data (x, y, value) VALUES (?, ?, ?)', (x, y, value))
        conn.commit()
        conn.close()
        print(f'Fetched and stored {len(heatmap)} points.')
    except Exception as e:
        print(f'Error fetching/storing data: {e}')

if __name__ == '__main__':
    fetch_and_store()
