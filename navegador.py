import webbrowser
from urllib.parse import urlparse

class Navegador:
    def abrir_site(self, endereco, seguranca):
        endereco = str(endereco).strip()
        if len(endereco) > 500:
            return "Endereço muito longo."
        if "://" not in endereco:
            endereco = "https://" + endereco
        partes = urlparse(endereco)
        if partes.scheme != "https" or not partes.netloc:
            return "Por segurança, só abro endereços HTTPS válidos."
        if not seguranca.confirmar_acao(f"abrir o site {partes.netloc}"):
            return "Abertura cancelada."
        webbrowser.open_new_tab(endereco)
        return f"Abrindo {partes.netloc}."
