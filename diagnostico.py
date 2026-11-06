from sistema import Sistema
from processos import Processos

class Diagnostico:
    def __init__(self):
        self.sistema = Sistema()
        self.processos = Processos()

    def executar(self):
        return self.sistema.resumo() + "\n" + self.processos.resumo()
