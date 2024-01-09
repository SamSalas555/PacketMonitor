# trap_handler.py
from pysnmp.entity import engine, config
from pysnmp.carrier.asyncore.dgram import udp
from pysnmp.entity.rfc3413 import ntfrcv
import logging

filtered_values = set()

def add_filter(host, interface):
    print("Añadiendo filtro")
    filtered_values.add((host, interface))
    print(filtered_values)

def remove_filter(host, interface):
    filtered_values.discard((host, interface))

def is_filtered(host, interface):
    return (host, interface) in filtered_values

def start_trap_listener():
    snmpEngine = engine.SnmpEngine()

    TrapAgentAddress = '192.168.0.10'
    Port = 162

    logging.basicConfig(filename='traps_recibidas.log', filemode='w', format='%(asctime)s - %(message)s', level=logging.INFO)

    logging.info("El gestor está escuchando SNMP Traps en " + TrapAgentAddress + ", Puerto : " + str(Port))
    logging.info('--------------------------------------------------------------------------')

    config.addTransport(
        snmpEngine,
        udp.domainName + (1,),
        udp.UdpTransport().openServerMode((TrapAgentAddress, Port))
    )

    config.addV1System(snmpEngine, 'public', 'public')

    def cbFun(snmpEngine, stateReference, contextEngineId, contextName, varBinds, cbCtx):
        print("Nuevo mensaje de traps recibido")
        logging.info("Nuevo mensaje de traps recibido")

        for name, val in varBinds:
            if val.prettyPrint() in [interface for _, interface in filtered_values]:
                logging.info("Ignorando mensaje debido a filtro")
                return

        for name, val in varBinds:
            logging.info('%s = %s' % (name.prettyPrint(), val.prettyPrint()))
            print('%s = %s' % (name.prettyPrint(), val.prettyPrint()))

        logging.info("==== Fin del mensaje de la trampa ====")

    ntfrcv.NotificationReceiver(snmpEngine, cbFun)

    snmpEngine.transportDispatcher.jobStarted(1)

    try:
        snmpEngine.transportDispatcher.runDispatcher()
    except:
        snmpEngine.transportDispatcher.closeDispatcher()
        raise
