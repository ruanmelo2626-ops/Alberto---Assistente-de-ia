import pyautogui

TECLAS_PERMITIDAS = {
    "enter", "esc", "tab", "space", "backspace", "delete",
    "up", "down", "left", "right", "home", "end",
    "pageup", "pagedown", "f1", "f2", "f3", "f4", "f5",
}
ATALHOS_PERMITIDOS = {
    "ctrl+c": ["ctrl", "c"],
    "ctrl+v": ["ctrl", "v"],
    "ctrl+x": ["ctrl", "x"],
    "ctrl+z": ["ctrl", "z"],
    "ctrl+a": ["ctrl", "a"],
    "ctrl+s": ["ctrl", "s"],
    "alt+tab": ["alt", "tab"],
    "win+d": ["win", "d"],
}

class ControleTeclado:
    def __init__(self, seguranca):
        self.seguranca = seguranca
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.25

    def digitar_texto(self, texto):
        if not isinstance(texto, str) or not texto or len(texto) > 500:
            return "Texto inválido ou muito longo (máximo 500 caracteres)."
        if not self.seguranca.confirmar_acao("digitar texto no aplicativo ativo"):
            return "Digitação cancelada."
        try:
            import pyperclip
            pyperclip.copy(texto)
            pyautogui.hotkey("ctrl", "v")
        except ImportError:
            if not texto.isascii():
                return "Para digitar caracteres especiais, instale pyperclip: python -m pip install pyperclip"
            pyautogui.write(texto, interval=0.02)
        return "Texto enviado ao aplicativo ativo."

    def pressionar_tecla(self, tecla):
        tecla = str(tecla).strip().lower()
        if tecla not in TECLAS_PERMITIDAS:
            return "Tecla não permitida."
        if not self.seguranca.confirmar_acao(f"pressionar {tecla}"):
            return "Ação cancelada."
        pyautogui.press(tecla)
        return "Tecla pressionada."

    def executar_atalho(self, atalho):
        teclas = ATALHOS_PERMITIDOS.get(str(atalho).lower())
        if not teclas:
            return "Atalho não permitido."
        if not self.seguranca.confirmar_acao(f"executar o atalho {atalho}"):
            return "Atalho cancelado."
        pyautogui.hotkey(*teclas)
        return "Atalho executado."
