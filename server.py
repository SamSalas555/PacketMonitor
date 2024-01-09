from flask import Flask, jsonify,Response
from pysnmptraps import start_trap_listener, add_filter, remove_filter
import threading
import time
import trafic as tif
import json
import graficas as tgraph
app = Flask(__name__)

hosts ={
    'TDR-1':'192.168.0.1',
    'TDR-2':'192.168.10.1',
    'R1':'10.10.10.17',
    'R2':'10.10.10.21',
    'Edge':'10.10.10.1',
    'ISP':'20.20.20.1',
} 


interfaces = {
    'fa0/0': 1,
    'fa1/0': 2,
    'fa1/1': 3,
    'fa2/0': 4,
    'fa2/1': 5,
    'fa3/0': 6,
    'fa3/1': 7,
    'fa4/0': 8,
    'fa4/1': 9,
    'fa5/0': 10,
    'fa5/1': 11,
    'fa6/0': 12,
    'fa6/1': 13,
}

interfaces_routes = {
    'fa0-0': 'fa0/0',
    'fa1-0': 'fa1/0',
    'fa1-1': 'fa1/1',
    'fa2-0': 'fa2/0',  
    'fa2-1': 'fa2/1',
    'fa3-0': 'fa3/0',
    'fa3-1': 'fa3/1',
    'fa4-0': 'fa4/0',
    'fa4-1': 'fa4/1',
    'fa5-0': 'fa5/0',
    'fa5-1': 'fa5/1',
    'fa6-0': 'fa6/0',
    'fa6-1': 'fa6/1',
}
full_interfaces_routes = {
    'fa0-0': 'FastEthernet0/0',
    'fa1-0': 'FastEthernet1/0',
    'fa1-1': 'FastEthernet1/1',
    'fa2-0': 'FastEthernet2/0',
    'fa2-1': 'FastEthernet2/1',
    'fa3-0': 'FastEthernet3/0',
    'fa3-1': 'FastEthernet3/1',
    'fa4-0': 'FastEthernet4/0',
    'fa4-1': 'FastEthernet4/1',
    'fa5-0': 'FastEthernet5/0',
    'fa5-1': 'FastEthernet5/1',
    'fa6-0': 'FastEthernet6/0',
    'fa6-1': 'FastEthernet6/1',
}




# Diccionario para almacenar los estados y bloqueos de cada demonio
daemon_states = {}
daemon_locks = {}

def daemon(host, interface, seconds):
    end_time = time.time() + seconds
    daemon_states[(host, interface)] = True
    daemon_locks[(host, interface)] = threading.Lock()
    print(daemon_locks)
    print(daemon_states)

    while time.time() < end_time and daemon_states[(host, interface)]:
        start_time = time.time()
        print(f"Ejecutado para {host} - {interface} en {start_time}")
        result = tif.get_traffic(host, interfaces_routes[interface])
        time.sleep(10)  # Dormir durante 1 segundo en cada iteración


def start_trap_listener_thread():
    thread = threading.Thread(target=start_trap_listener)
    thread.daemon = True
    thread.start()

@app.route('/routers/<hostname>/interfaces/<interface>/octetos/', methods=['GET'])
def get_octet_samples(hostname, interface):
    file_path = f'Data/{hostname}{interface}.txt'

    try:
        with open(file_path, 'r') as file:
            data = []
            for line in file:
                try:
                    json_data = json.loads(line)
                    data.append(json_data)
                except json.JSONDecodeError as e:
                    print(f"Error al cargar JSON en línea: {line.strip()}. Detalles: {e}")

            return jsonify(data)
    except FileNotFoundError:
        return jsonify({'error': 'Archivo no encontrado'}), 404

@app.route('/routers/<hostname>/interfaces/<interface>/octetos/<tiempo>', methods=['POST'])
def activate_octet_monitoring(hostname, interface, tiempo):
    global daemon_states

    if (hostname, interface) in daemon_states and daemon_states[(hostname, interface)]:
        return jsonify({'error': 'Ya existe un demonio en ejecución para este host e interfaz'}), 400

    try:
        tiempo_segundos = float(tiempo)
    except ValueError:
        return jsonify({'error': 'Tiempo ingresado no es un número válido'}), 400

    # Start the demon thread
    daemon_thread = threading.Thread(target=daemon, args=(hosts[hostname], interface, tiempo_segundos))
    daemon_thread.start()

    return jsonify({'Estado': 'Activo', 'Tiempo': tiempo_segundos})

# Endpoint para detener el monitoreo de octetos de interfaz
@app.route('/routers/<hostname>/interfaces/<interface>/octetos/', methods=['DELETE'])
def stop_octet_monitoring(hostname, interface):
    global daemon_states

    with daemon_locks[(hosts[hostname], interface)]:
        daemon_states[(hosts[hostname], interface)] = False

    return jsonify({'hostname': hostname, 'interface': interface, 'estado': 'detenido'})




# Endpoint para obtener el estado de la interfaz
@app.route('/routers/<hostname>/interfaces/<interface>/estado', methods=['GET'])
def get_interface_status(hostname, interface):
    return jsonify(tif.get_status(hosts[hostname], interfaces_routes[interface]))

# Endpoint para activar la captura de trampas de una interfaz
@app.route('/routers/<hostname>/interfaces/<interface>/estado', methods=['POST'])
def activate_traps(hostname, interface):
    remove_filter(hosts[hostname], full_interfaces_routes[interface])
    print("Añadiendo filtro")
    return jsonify(tif.get_status(hosts[hostname], interfaces_routes[interface]))

# Endpoint para desactivar la captura de trampas de una interfaz
@app.route('/routers/<hostname>/interfaces/<interface>/estado', methods=['DELETE'])
def deactivate_traps(hostname, interface):
    add_filter(hosts[hostname], full_interfaces_routes[interface])
    print("Añadiendo filtro")
    return jsonify(tif.get_status(hosts[hostname], interfaces_routes[interface]))



###Zona de graficas

# Define the Flask endpoint
@app.route('/routers/<hostname>/interfaces/<interface>/grafica/octetos', methods=['GET'])
def traffic(hostname, interface):
    try: 
        if interface in interfaces_routes:
            return Response(tgraph.grafic_interface(hostname,interface), content_type='image/svg+xml')
        else:
            return jsonify({'status': 'error', 'message': 'Invalid interface'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'No Data'}), 404
    
@app.route('/routers/<hostname>/interfaces/<interface>/grafica/estado', methods=['GET'])
def trap_graphs(hostname, interface):
    try: 
        if interface in interfaces_routes:
            return Response(tgraph.grafic_traps(hosts[hostname] ,full_interfaces_routes[interface]), content_type='image/svg+xml')
        else:
            return jsonify({'status': 'error', 'message': 'Invalid interface'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'No Data'}), 404



if __name__ == '__main__':
    start_trap_listener_thread()
    app.run(debug=True)
