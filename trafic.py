from pysnmp.entity.rfc3413.oneliner import cmdgen
import datetime

cmdGen = cmdgen.CommandGenerator()

host = '192.168.8.1'
community = 'public'

# Hostname OID
system_name = '1.3.6.1.2.1.1.5.0'

# Interface OID
in_uPackets = '1.3.6.1.2.1.2.2.1.11.'
out_uPackets = '1.3.6.1.2.1.2.2.1.17.'


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

interfaces={
    'fa0/0':0,
    'fa0/1':1,
    'fa1/1':2
}

def get_traffic(interface):
    result = {}
    result['Tiempo'] = datetime.datetime.utcnow().isoformat()
    result['hostname'] = snmp_query(host, community, system_name)
    in_uPackets_query = snmp_query(host, community, in_uPackets + str(interfaces[interface]))
    out_uPackets_query = snmp_query(host, community, out_uPackets + str(interfaces[interface]))

    # Check if the result is empty, and set to 0 if it is
    result[interface + '_In_uPackets'] = float(in_uPackets_query) if in_uPackets_query else 0
    result[interface + '_Out_uPackets'] = float(out_uPackets_query) if out_uPackets_query else 0

    with open('./Data/traffic'+str(interfaces[interface])+'.txt', 'a') as f:
        f.write(str(result))
        f.write('\n')

