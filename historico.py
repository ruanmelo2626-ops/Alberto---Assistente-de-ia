import json
import threading

from configuracoes import PASTA_MEMORIA, LIMITE_HISTORICO


class Historico:
    def __init__(self):
        self.arquivo = PASTA_MEMORIA / "conversa.json"
        self.lock = threading.RLock()

        PASTA_MEMORIA.mkdir(parents=True, exist_ok=True)

        self.mensagens = self._carregar()

    def _carregar(self):
        try:
            dados = json.loads(
                self.arquivo.read_text(encoding="utf-8")
            )

            if not isinstance(dados, list):
                return []

            mensagens = []

            for item in dados:
                if not isinstance(item, dict):
                    continue

                papel = item.get("role")
                conteudo = item.get("content")

                if papel not in {"user", "assistant"}:
                    continue

                if not isinstance(conteudo, str) or not conteudo.strip():
                    continue

                mensagens.append({
                    "role": papel,
                    "content": conteudo[:6000]
                })

            return mensagens[-LIMITE_HISTORICO * 2:]

        except (OSError, json.JSONDecodeError):
            return []

    def _salvar(self):
        temporario = self.arquivo.with_suffix(".tmp")

        temporario.write_text(
            json.dumps(
                self.mensagens,
                ensure_ascii=False,
                indent=2
            ),
            encoding="utf-8"
        )

        temporario.replace(self.arquivo)

    def adicionar(self, papel, conteudo):
        if papel not in {"user", "assistant"}:
            return

        conteudo = str(conteudo).strip()

        if not conteudo:
            return

        with self.lock:
            self.mensagens.append({
                "role": papel,
                "content": conteudo[:6000]
            })

            limite = max(1, LIMITE_HISTORICO) * 2
            self.mensagens = self.mensagens[-limite:]

            try:
                self._salvar()
            except OSError as erro:
                print(f"Falha ao salvar histórico: {erro}")

    def obter(self, limite=None, max_caracteres=None):
        with self.lock:
            mensagens = list(self.mensagens)

        if limite is not None:
            mensagens = mensagens[-limite:]

        if max_caracteres is not None:
            resultado = []
            total = 0

            for mensagem in reversed(mensagens):
                tamanho = len(mensagem["content"])

                if total + tamanho > max_caracteres:
                    restante = max_caracteres - total

                    if restante <= 0:
                        break

                    mensagem = {
                        "role": mensagem["role"],
                        "content": mensagem["content"][-restante:]
                    }

                    tamanho = restante

                resultado.append(mensagem)
                total += tamanho

            mensagens = list(reversed(resultado))

        return mensagens

    def limpar(self, seguranca):
        if not seguranca.confirmar_acao(
            "apagar o histórico de conversas"
        ):
            return False

        with self.lock:
            self.mensagens = []

            try:
                self._salvar()
                return True
            except OSError:
                return False