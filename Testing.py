import requests as r
import json
import time
import numpy as np
from http.server import BaseHTTPRequestHandler, HTTPServer
import matplotlib.pyplot as plt


# Define the port on which the server will listen
PORT = 8000

class RequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        acc_data = phyphox_data()
        data = {
            'acc': acc_data['acc'],
            'accX': acc_data['accX'],
            'accY': acc_data['accY'],
            'accZ': acc_data['accZ']
        }
        self.wfile.write(json.dumps(data).encode())

def phyphox_data():
    global start_time
    response = r.get(url + '&'.join(what_to_get)).text
    data = json.loads(response)
    
    acc_data = data['buffer'][what_to_get[0]]['buffer'][0]
    acc_dataX = data['buffer'][what_to_get[1]]['buffer'][0]
    acc_dataY = data['buffer'][what_to_get[2]]['buffer'][0]
    acc_dataZ = data['buffer'][what_to_get[3]]['buffer'][0]
    
    # Apply high pass filter to data
    if acc_data < 0.09:
        acc_data = 0
    if acc_dataX < 0.09:
        acc_dataX = 0
    if acc_dataY < 0.09:
        acc_dataY = 0
    if acc_dataZ < 0.09:
        acc_dataZ = 0
    current_time = time.time() - start_time

    # Append data to dictionary
    data_dict[current_time] = {'acc': acc_data, 'accX': acc_dataX, 'accY': acc_dataY, 'accZ': acc_dataZ}
    
    print(f'Time: {current_time:.2f}s, Acceleration: {acc_data}')
    return data_dict[current_time]

def fastFourierTransform(time_acc_dict):
    # Extract time and acceleration values from the dictionary
    time_values = np.array(list(time_acc_dict.keys()))
    acceleration_values = np.array([data['acc'] for data in time_acc_dict.values()])

    # Compute the FFT of acceleration values
    fft_result = np.fft.fft(acceleration_values)

    # Compute the corresponding frequencies
    dt = time_values[1] - time_values[0]  # Assuming uniform time spacing
    frequencies = np.fft.fftfreq(len(time_values), dt)

    return frequencies, fft_result

# Define additional variables and parameters
start_time = time.time()
data_dict = {}
movement_detected = False
movement_times = []
sampling_interval = 0.1  # Sampling interval in seconds
url = 'http://172.20.10.1/get?'
what_to_get = ['acc', 'accX', 'accY', 'accZ']

def run(server_class=HTTPServer, handler_class=RequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting server on port {port}')
    httpd.serve_forever()
# Start the server in a separate thread
import threading
server_thread = threading.Thread(target=run, kwargs={'port': PORT})
server_thread.daemon = True
server_thread.start()

# Collect data for a certain duration
duration = 5  # Duration in seconds
end_time = start_time + duration

while time.time() < end_time:
    acc_data = phyphox_data()
    
    if acc_data['acc'] > 0.1:
        if not movement_detected:
            movement_times.append(time.time()-start_time)
            movement_detected = True
    else:
        movement_detected = False

    time.sleep(sampling_interval-0.01)

# Perform FFT on the collected data
returned_frequencies, returned_fft_result = fastFourierTransform(data_dict)

# Remove the first item from the arrays
returned_frequencies = returned_frequencies[1:]
returned_fft_result = returned_fft_result[1:]
power_spectrum = np.abs(returned_fft_result)**2

# Find the index of the maximum power frequency
max_power_freq_index = np.argmax(power_spectrum)
max_power_freq = returned_frequencies[max_power_freq_index]

# Calculate time intervals between consecutive movements at the maximum power frequency
movement_intervals = np.diff(movement_times)

print("Power Spectrum:")
print(power_spectrum)
print(returned_frequencies)
print("Max Power Frequency:", max_power_freq, "Hz")
print("Time Intervals between Movements at Max Power Frequency:", movement_intervals)
print(movement_times)
