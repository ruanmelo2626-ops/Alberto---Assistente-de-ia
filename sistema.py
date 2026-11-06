import platform
import socket
import psutil
from datetime import datetime

class Sistema:
    def resumo(self):
        memoria = psutil.virtual_memory()
        raiz = __import__("os").path.abspath(__import__("os").sep)
        disco = psutil.disk_usage(raiz)
        return (
            f"Sistema: {platform.system()} {platform.release()}\n"
            f"Computador: {platform.node()}\n"
            f"Processador: {platform.processor() or 'Não identificado'}\n"
            f"CPU em uso: {psutil.cpu_percent(interval=0.5)}%\n"
            f"Memória RAM: {memoria.percent}% utilizada "
            f"({memoria.used / 1024**3:.1f}/{memoria.total / 1024**3:.1f} GB)\n"
            f"Disco: {disco.percent}% utilizado\n"
            f"Rede: {socket.gethostname()}\n"
            f"Data/hora: {datetime.now():%d/%m/%Y %H:%M:%S}"
        )

    def obter_horario(self):
        return datetime.now().strftime("%H:%M")

    def obter_data(self):
        return datetime.now().strftime("%d/%m/%Y")
