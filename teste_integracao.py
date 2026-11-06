from seguranca import Seguranca
from sistema import Sistema
from processos import Processos
from memoria import Memoria
from inteligencia import Inteligencia

print("Segurança:", Seguranca())
print("Sistema:", Sistema().obter_horario())
print("Processos:", Processos().resumo())
print("Memória:", Memoria().listar())
print("Integração básica concluída.")
