from seguranca import Seguranca
from controle_mouse import ControleMouse

mouse = ControleMouse(Seguranca())
print(mouse.obter_posicao())
print(mouse.mover(100, 100))
