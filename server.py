from flask import Flask, jsonify,Response
import threading
import time
import trafic as tif
import graficas as tgraph

app = Flask(__name__)

interfaces = {
    'fa0/0': 0,
    'fa0/1': 1,
    'fa1/1': 2
}
interfaces_routes = {
    'fa0-0': 'fa0/0',
    'fa0-1': 'fa0/1',
    'fa1-1': 'fa1/1'
}

def daemon():
    while True:
        start_time = time.time()
		
        for interface in interfaces:
            print("Ejecutado"+ str(start_time))
            result = tif.get_traffic(interface)
            # Realizar acciones adicionales con el resultado si es necesario

        elapsed_time = time.time() - start_time
        sleep_time = max(0, 20 - elapsed_time)  # Asegurarse de que sleep_time sea al menos 0

        time.sleep(sleep_time)

# Start the daemon thread
daemon_thread = threading.Thread(target=daemon)
daemon_thread.start()

# Define the Flask endpoint
@app.route('/traffic/<interface>', methods=['GET'])
def traffic(interface):
    if interface in interfaces_routes:
        return Response(tgraph.grafic_interface(interfaces_routes[interface]), content_type='image/svg+xml')
    else:
        return jsonify({'status': 'error', 'message': 'Invalid interface'}), 404

if __name__ == '__main__':
    app.run(debug=True)
