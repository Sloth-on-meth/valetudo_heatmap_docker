import os
import requests
from dotenv import load_dotenv
import db
import base64
from io import BytesIO
from PIL import Image

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

VALETUDO_HOST = os.getenv('VALETUDO_HOST')
VALETUDO_API_PATH = os.getenv('VALETUDO_API_PATH', '/api/v2/robot/capabilities/Map')

if VALETUDO_HOST:
    VALETUDO_API_URL = f'http://{VALETUDO_HOST}{VALETUDO_API_PATH}'
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
        # Valetudo v2022+ returns a base64-encoded PNG/PGM in data['result']['map']
        map_b64 = data.get('result', {}).get('map')
        if not map_b64:
            print('No map data found in response')
            return
        img_bytes = base64.b64decode(map_b64)
        img = Image.open(BytesIO(img_bytes)).convert('RGB')
        width, height = img.size
        pixels = img.load()
        heatmap_points = []
        for y in range(height):
            for x in range(width):
                r, g, b = pixels[x, y]
                # Heuristic: cleaned/covered area is usually white or near-white
                if r > 200 and g > 200 and b > 200:
                    heatmap_points.append({'x': x, 'y': y, 'value': 1})
        conn = db.get_db_connection()
        cur = conn.cursor()
        for point in heatmap_points:
            cur.execute('INSERT INTO robot_data (x, y, value) VALUES (?, ?, ?)', (point['x'], point['y'], point['value']))
        conn.commit()
        conn.close()
        print(f'Fetched and stored {len(heatmap_points)} heatmap points.')
    except Exception as e:
        print(f'Error fetching/storing data: {e}')

if __name__ == '__main__':
    fetch_and_store()
