import json
from pathlib import Path
from configuracoes import PASTA_MEMORIA, LIMITE_HISTORICO

class Historico:
    def __init__(self):
        self.arquivo = PASTA_MEMORIA / "conversa.json"
        PASTA_MEMORIA.mkdir(parents=True, exist_ok=True)
        self.mensagens = self._carregar()

    def _carregar(self):
        try:
            dados = json.loads(self.arquivo.read_text(encoding="utf-8"))
            return dados if isinstance(dados, list) else []
        except (OSError, json.JSONDecodeError):
            return []

    def adicionar(self, papel, conteudo):
        self.mensagens.append({"role": papel, "content": str(conteudo)})
        self.mensagens = self.mensagens[-LIMITE_HISTORICO * 2:]
        self.arquivo.write_text(
            json.dumps(self.mensagens, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def obter(self):
        return list(self.mensagens)

    def limpar(self, seguranca):
        if not seguranca.confirmar_acao("apagar o histórico de conversas"):
            return False
        self.mensagens = []
        self.arquivo.write_text("[]", encoding="utf-8")
        return True
