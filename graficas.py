import pygal
from datetime import datetime
x_time = []
out_packets = []
in_packets = []

interfaces = {
    'fa0/0': 0,
    'fa0/1': 1,
    'fa1/1': 2
}

def grafic_interface(interface):
    x_time = []
    out_pps = []
    in_pps = []

    with open(f'./Data/traffic{interfaces[interface]}.txt', 'r') as f:
        previous_time = None
        previous_out_packets = 0
        previous_in_packets = 0

        for line in f.readlines():
            line = eval(line)
            current_time = line['Tiempo']
            current_out_packets = float(line[interface + '_Out_uPackets'])
            current_in_packets = float(line[interface + '_In_uPackets'])

            if previous_time is not None:
                time_diff = (datetime.fromisoformat(current_time) - datetime.fromisoformat(previous_time)).total_seconds()
                out_pps.append((current_out_packets - previous_out_packets) / time_diff)
                in_pps.append((current_in_packets - previous_in_packets) / time_diff)

            x_time.append(current_time)
            previous_time = current_time
            previous_out_packets = current_out_packets
            previous_in_packets = current_in_packets

    line_chart = pygal.Line()
    line_chart.title = interface
    line_chart.x_labels = x_time
    line_chart.add('Paq. salida (pps)', out_pps)
    line_chart.add('Paq. entrada (pps)', in_pps)
    return line_chart.render()
