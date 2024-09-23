from flask import Flask, jsonify
import requests
import numpy as np

app = Flask(__name__)

@app.route('/data')
def get_data():
    try:
        response = requests.get('https://us-central1-fleetwood-cosine-384822.cloudfunctions.net/sleep_data')
        data = response.json()

        time = np.array([float(item['time']) for item in data])
        acc_x = np.array([float(item['acceleration_x']) for item in data])
        acc_y = np.array([float(item['acceleration_y']) for item in data])
        acc_z = np.array([float(item['acceleration_z']) for item in data])

        mean_x = np.mean(acc_x)
        mean_y = np.mean(acc_y)
        mean_z = np.mean(acc_z)

        accel_x = acc_x - mean_x
        accel_y = acc_y - mean_y
        accel_z = acc_z - mean_z

        abs_accel = np.sqrt(accel_x**2 + accel_y**2 + accel_z**2).tolist()

        return jsonify({'abs_accel': abs_accel, 'time': time.tolist()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
