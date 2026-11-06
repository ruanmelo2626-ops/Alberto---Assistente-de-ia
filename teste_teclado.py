from seguranca import Seguranca
from controle_teclado import ControleTeclado

teclado = ControleTeclado(Seguranca())
print(teclado.pressionar_tecla("esc"))
