class TrapSNMP:
    def __init__(self, address, interfaz, estado, hora):
        self.address = address
        self.interfaz = interfaz
        self.estado = estado
        self.hora = hora

    def __str__(self):
        return f"Direccion: {self.address}  Interfaz: {self.interfaz}\nEstado: {self.estado}\nHora: {self.hora}\n==="


def get_trapsf(nombre_archivo):
    traps = []
    interfaz = None
    estado = None

    with open(nombre_archivo, "r") as file:
        lines = file.readlines()
        for line in lines:
            if "1.3.6.1.2.1.2.2.1.2." in line:
                partes = line.split("=")
                interfaz = partes[1].strip()
            elif "1.3.6.1.6.3.18.1.3.0 ="in line:
                partes = line.split("=")
                address = partes[1].strip()
            elif "1.3.6.1.4.1.9.2.2.1.1.20" in line:
                partes = line.split("=")
                estado = partes[1].strip()
                hora = line.split(" ")[0] + " "+line.split(" ")[1]
                traps.append(TrapSNMP(address,interfaz, estado, hora))

    return traps

