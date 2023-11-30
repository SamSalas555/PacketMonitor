class TrapSNMP:
    def __init__(self, interfaz, estado, hora):
        self.interfaz = interfaz
        self.estado = estado
        self.hora = hora

    def __str__(self):
        return f"Interfaz: {self.interfaz}\nEstado: {self.estado}\nHora: {self.hora}\n==="


def get_trapsf(nombre_archivo):
    traps = []
    interfaz = None
    estado = None

    with open(nombre_archivo, "r") as file:
        lines = file.readlines()
        for line in lines:
            if "1.3.6.1.2.1.2.2.1.2.1 =" in line:
                partes = line.split("=")
                interfaz = partes[1].strip()
            elif "1.3.6.1.4.1.9.2.2.1.1.20.1 =" in line:
                partes = line.split("=")
                estado = partes[1].strip()
                hora = line.split(" ")[0] + " "+line.split(" ")[1]
                traps.append(TrapSNMP(interfaz, estado, hora))

    return traps


