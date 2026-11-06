from seguranca import Seguranca
from controle_computador import ControleComputador

pc = ControleComputador(Seguranca())
print(pc.resolucao_tela())
print(pc.posicao_mouse())
