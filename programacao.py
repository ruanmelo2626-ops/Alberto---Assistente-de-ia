from arquivos import criar_arquivo, ler_arquivo, listar_arquivos

class Programacao:
    """Ajuda a organizar arquivos de código sem executar código recebido."""

    EXTENSOES = {".py", ".html", ".css", ".js", ".json", ".txt", ".md", ".cpp", ".c"}

    def salvar_codigo(self, nome, codigo, seguranca):
        from pathlib import PurePath
        if PurePath(nome).suffix.lower() not in self.EXTENSOES:
            return "Extensão não permitida para este módulo."
        return criar_arquivo(nome, codigo, seguranca)

    def ler_codigo(self, nome):
        return ler_arquivo(nome)

    def listar_projetos(self):
        return listar_arquivos()
