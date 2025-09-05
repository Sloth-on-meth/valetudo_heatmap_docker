import os
import requests
from dotenv import load_dotenv
import db
import base64
from io import BytesIO
from PIL import Image

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

VALETUDO_HOST = os.getenv('VALETUDO_HOST')
# Default to MapSnapshot endpoint for latest Valetudo
VALETUDO_API_PATH = os.getenv('VALETUDO_API_PATH', '/api/v2/robot/capabilities/MapSnapshot')

if VALETUDO_HOST:
    VALETUDO_API_URL = f'http://{VALETUDO_HOST}{VALETUDO_API_PATH}'
else:
    VALETUDO_API_URL = None

def fetch_and_store():
    if not VALETUDO_API_URL:
        print('VALETUDO_HOST not set in .env')
        return
    try:
        # Step 1: Get the list of all snapshots
        resp = requests.get(VALETUDO_API_URL, timeout=10)
        resp.raise_for_status()
        snapshots = resp.json()
        if not isinstance(snapshots, list):
            print('Unexpected response for snapshot list')
            return
        print(f'Found {len(snapshots)} map snapshots.')
        total_points = 0
        for snap in snapshots:
            snap_id = snap.get('id')
            if not snap_id:
                continue
            snap_url = f'{VALETUDO_API_URL}/{snap_id}'
            snap_resp = requests.get(snap_url, timeout=10)
            snap_resp.raise_for_status()
            snap_data = snap_resp.json()
            map_b64 = snap_data.get('result', {}).get('png')
            if not map_b64:
                print(f'No map image found in snapshot {snap_id}')
                continue
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
                        heatmap_points.append({'x': x, 'y': y, 'value': 1, 'snapshot_id': snap_id})
            conn = db.get_db_connection()
            cur = conn.cursor()
            for point in heatmap_points:
                cur.execute('INSERT INTO robot_data (x, y, value) VALUES (?, ?, ?)', (point['x'], point['y'], point['value']))
            conn.commit()
            conn.close()
            print(f'Snapshot {snap_id}: stored {len(heatmap_points)} heatmap points.')
            total_points += len(heatmap_points)
        print(f'Total heatmap points stored from all snapshots: {total_points}')
    except Exception as e:
        print(f'Error fetching/storing data: {e}')

if __name__ == '__main__':
    fetch_and_store()
