from arquivos import criar_arquivo, ler_arquivo, listar_arquivos

class GerenciadorArquivos:
    """Interface organizada para operações limitadas ao workspace."""

    def criar(self, nome, conteudo="", seguranca=None):
        return criar_arquivo(nome, conteudo, seguranca)

    def ler(self, nome):
        return ler_arquivo(nome)

    def listar(self):
        return listar_arquivos()
