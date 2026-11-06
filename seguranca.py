import logging
from pathlib import Path
from datetime import datetime
from configuracoes import PASTA_TRABALHO, PASTA_LOGS

class Seguranca:
    """Centraliza confirmações, validação de caminhos e registros."""

    def __init__(self):
        PASTA_LOGS.mkdir(parents=True, exist_ok=True)
        self.arquivo_log = PASTA_LOGS / "alberto.log"
        logging.basicConfig(
            filename=str(self.arquivo_log),
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | %(message)s",
            encoding="utf-8",
            force=True,
        )

    def registrar(self, mensagem):
        logging.info(str(mensagem))

    def registrar_erro(self, mensagem):
        logging.exception(str(mensagem))

    def confirmar_acao(self, descricao):
        print(f"\nALBERTO deseja: {descricao}")
        resposta = input("Digite CONFIRMAR para autorizar: ").strip()
        autorizado = resposta == "CONFIRMAR"
        self.registrar(f"Ação {'autorizada' if autorizado else 'recusada'}: {descricao}")
        return autorizado

    def validar_caminho(self, caminho):
        base = PASTA_TRABALHO.resolve()
        caminho = Path(caminho)
        if caminho.is_absolute():
            raise ValueError("Informe um caminho relativo à pasta workspace.")
        destino = (base / caminho).resolve()
        if destino != base and base not in destino.parents:
            raise ValueError("Acesso negado: caminho fora da pasta workspace.")
        return destino

    def verificar_arquivo(self, caminho):
        return self.validar_caminho(caminho).is_file()

    def verificar_pasta(self, caminho):
        return self.validar_caminho(caminho).is_dir()

    def consultar_logs(self, limite=40):
        if not self.arquivo_log.exists():
            return "Ainda não existem registros."
        linhas = self.arquivo_log.read_text(encoding="utf-8", errors="replace").splitlines()
        return "\n".join(linhas[-max(1, min(limite, 200)):])

    @staticmethod
    def obter_horario():
        return datetime.now().strftime("%d/%m/%Y %H:%M:%S")
