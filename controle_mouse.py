import pyautogui

class ControleMouse:
    def __init__(self, seguranca):
        self.seguranca = seguranca
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.25

    def obter_posicao(self):
        p = pyautogui.position()
        return f"Mouse na posição X={p.x}, Y={p.y}."

    def mover(self, x, y):
        largura, altura = pyautogui.size()
        if not (0 <= x < largura and 0 <= y < altura):
            return "Coordenadas fora da tela."
        if not self.seguranca.confirmar_acao(f"mover o mouse para ({x}, {y})"):
            return "Movimento cancelado."
        pyautogui.moveTo(x, y, duration=0.3)
        return "Mouse movido."

    def clicar(self, x=None, y=None, botao="left"):
        if botao not in ("left", "right", "middle"):
            return "Botão inválido."
        if (x is None) != (y is None):
            return "Informe as duas coordenadas ou nenhuma delas."
        if x is not None:
            largura, altura = pyautogui.size()
            if not (isinstance(x, int) and isinstance(y, int) and 0 <= x < largura and 0 <= y < altura):
                return "Coordenadas fora da tela ou inválidas."
        if not self.seguranca.confirmar_acao("clicar com o mouse"):
            return "Clique cancelado."
        pyautogui.click(x=x, y=y, button=botao)
        return "Clique realizado."

    def duplo_clique(self, x=None, y=None):
        if not self.seguranca.confirmar_acao("dar um duplo clique"):
            return "Ação cancelada."
        pyautogui.doubleClick(x=x, y=y)
        return "Duplo clique realizado."

    def rolar(self, quantidade):
        quantidade = max(-10, min(10, int(quantidade)))
        if not self.seguranca.confirmar_acao("rolar a página"):
            return "Rolagem cancelada."
        pyautogui.scroll(quantidade)
        return "Rolagem realizada."
