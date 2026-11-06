import pyautogui
from configuracoes import PASTA_CAPTURAS
from controle_mouse import ControleMouse
from controle_teclado import ControleTeclado

class ControleComputador:
    """Fachada que reúne mouse, teclado e captura de tela."""

    def __init__(self, seguranca):
        self.seguranca = seguranca
        self.mouse = ControleMouse(seguranca)
        self.teclado = ControleTeclado(seguranca)
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.25

    def resolucao_tela(self):
        w, h = pyautogui.size()
        return f"Resolução: {w} x {h}"

    def posicao_mouse(self):
        return self.mouse.obter_posicao()

    def captura_tela(self):
        if not self.seguranca.confirmar_acao("capturar a tela"):
            return "Captura cancelada."
        PASTA_CAPTURAS.mkdir(parents=True, exist_ok=True)
        arquivo = PASTA_CAPTURAS / "captura_alberto.png"
        pyautogui.screenshot().save(arquivo)
        self.seguranca.registrar(f"Captura de tela: {arquivo}")
        return f"Captura salva em {arquivo}"
