from pysnmp.entity.rfc3413.oneliner import cmdgen
import datetime
import json
cmdGen = cmdgen.CommandGenerator()

community = 'public'

# Hostname OID
system_name = '1.3.6.1.2.1.1.5.0'

# Interface OID
in_uPackets = '1.3.6.1.2.1.2.2.1.11.'
out_uPackets = '1.3.6.1.2.1.2.2.1.17.'

stat ='1.3.6.1.4.1.9.2.2.1.1.20.'


def snmp_query(host, community, oid):
    errorIndication, errorStatus, errorIndex, varBinds = cmdGen.getCmd(
        cmdgen.CommunityData(community),
        cmdgen.UdpTransportTarget((host, 161)),
        oid
    )
    
    # Revisamos errores e imprimimos resultados
    if errorIndication:
        print(errorIndication)
    else:
        if errorStatus:
            print('%s at %s' % (
                errorStatus.prettyPrint(),
                errorIndex and varBinds[int(errorIndex)-1] or '?'
                )
            )
        else:
            for name, val in varBinds:
                return(str(val))

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
    'fa0/0': 'fa0-0',
    'fa1/0': 'fa1-0',
    'fa1/1': 'fa1-1',
    'fa2/0': 'fa2-0',  # Puedes agregar más entradas si es necesario
    'fa2/1': 'fa2-1',
    'fa3/0': 'fa3-0',
    'fa3/1': 'fa3-1',
    'fa4/0': 'fa4-0',
    'fa4/1': 'fa4-1',
    'fa5/0': 'fa5-0',
    'fa5/1': 'fa5-1',
    'fa6/0': 'fa6-0',
    'fa6/1': 'fa6-1',
}

def get_traffic(host,interface):
    print(host + " " + interface)
    result = {}
    result['Tiempo'] = datetime.datetime.utcnow().isoformat()
    result['hostname'] = snmp_query(host, community, system_name)
    in_uPackets_query = snmp_query(host, community, in_uPackets + str(interfaces[interface]))
    out_uPackets_query = snmp_query(host, community, out_uPackets + str(interfaces[interface]))

    # Check if the result is empty, and set to 0 if it is
    result[interface + '_In_uPackets'] = float(in_uPackets_query) if in_uPackets_query else 0
    result[interface + '_Out_uPackets'] = float(out_uPackets_query) if out_uPackets_query else 0
    print(interface)
    
    with open('./Data/'+result['hostname']+str(interfaces_routes[interface])+'.txt', 'a') as f:
        json.dump(result, f)
        f.write('\n')

def get_status(host,interface):
    status = snmp_query(host, community, stat+ str(interfaces[interface]))
    return status