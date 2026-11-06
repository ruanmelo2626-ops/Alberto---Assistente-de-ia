from urllib.parse import quote_plus
import webbrowser

class Internet:
    def pesquisar(self, consulta):
        consulta = str(consulta).strip()
        if not consulta:
            return "Informe o que deseja pesquisar."
        url = "https://www.google.com/search?q=" + quote_plus(consulta[:300])
        webbrowser.open_new_tab(url)
        return "Pesquisa aberta no navegador."
