from seguranca import Seguranca
from controle_janelas import ControleJanelas

janelas = ControleJanelas(Seguranca())
print(janelas.listar_janelas())
print("Ativa:", janelas.obter_janela_ativa())
