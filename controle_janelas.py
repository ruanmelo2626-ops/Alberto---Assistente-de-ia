import pygetwindow as gw

class ControleJanelas:
    def __init__(self, seguranca):
        self.seguranca = seguranca

    def listar_janelas(self):
        titulos = [t for t in gw.getAllTitles() if t.strip()]
        return "\n".join(titulos[:40]) if titulos else "Nenhuma janela encontrada."

    def obter_janela_ativa(self):
        janela = gw.getActiveWindow()
        return janela.title if janela else "Não consegui identificar a janela ativa."

    def _encontrar(self, trecho):
        trecho = trecho.casefold()
        return next((j for j in gw.getAllWindows() if trecho in j.title.casefold()), None)

    def ativar(self, trecho):
        janela = self._encontrar(trecho)
        if not janela:
            return "Janela não encontrada."
        if not self.seguranca.confirmar_acao(f"ativar a janela {janela.title}"):
            return "Ação cancelada."
        try:
            janela.activate()
            return f"Janela ativada: {janela.title}"
        except Exception:
            return "Não consegui ativar essa janela."

    def minimizar(self, trecho):
        janela = self._encontrar(trecho)
        if not janela:
            return "Janela não encontrada."
        if not self.seguranca.confirmar_acao(f"minimizar a janela {janela.title}"):
            return "Ação cancelada."
        janela.minimize()
        return "Janela minimizada."

    def maximizar(self, trecho):
        janela = self._encontrar(trecho)
        if not janela:
            return "Janela não encontrada."
        if not self.seguranca.confirmar_acao(f"maximizar a janela {janela.title}"):
            return "Ação cancelada."
        janela.maximize()
        return "Janela maximizada."
