import pygal
from datetime import datetime
from trap_parser import get_trapsf
x_time = []
out_packets = []
in_packets = []

interfaces = {
    'fa0/0': 0,
    'fa0/1': 1,
    'fa1/1': 2
}

def grafic_interface(host,interface):
    x_time = []
    out_pps = []
    in_pps = []
    with open(f'./Data/{host}{interface}.txt', 'r') as f:
        previous_time = None
        previous_out_packets = 0
        previous_in_packets = 0

        for line in f.readlines():
            line = eval(line)
            current_time = line['Tiempo']
            print(datetime.fromisoformat(current_time))
            current_out_packets = float(line[interfaces_routes[interface] + '_Out_uPackets'])
            current_in_packets = float(line[interfaces_routes[interface]+ '_In_uPackets'])

            if previous_time is not None:
                time_diff = (datetime.fromisoformat(current_time) - datetime.fromisoformat(previous_time)).total_seconds()
                out_pps.append((current_out_packets - previous_out_packets) / time_diff)
                in_pps.append((current_in_packets - previous_in_packets) / time_diff)

            x_time.append(datetime.fromisoformat(current_time))
            previous_time = current_time
            previous_out_packets = current_out_packets
            previous_in_packets = current_in_packets

    line_chart = pygal.Line()
    line_chart.title = interface
    line_chart.x_labels = x_time
    line_chart.add('Paq. salida (pps)', out_pps)
    line_chart.add('Paq. entrada (pps)', in_pps)
    return line_chart.render()
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

def grafic_traps(host,interface):
    traps =  get_trapsf("traps_recibidas.log")
    time = []
    status = []
    for trap in traps:
        print(interface + "" + host)
        if (trap.interfaz == interface and trap.address == host):
            time.append(trap.hora)
            if(trap.estado != "administratively down"):
                status.append(5)
            else:
                status.append(0)

    status_chart = pygal.Line()
    status_chart.title="Alertas "+ interface
    status_chart.x_labels=time
    status_chart.add("Alertas",status)
    return status_chart.render()
