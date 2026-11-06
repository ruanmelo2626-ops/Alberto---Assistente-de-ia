import json
import urllib.request
import urllib.error

from configuracoes import (
    OLLAMA_URL,
    OLLAMA_MODELO,
    TIMEOUT_OLLAMA,
    OLLAMA_KEEP_ALIVE,
    OLLAMA_NUM_CTX,
    OLLAMA_NUM_THREAD,
    OLLAMA_MAX_TOKENS_RESPOSTA,
    OLLAMA_MAX_TOKENS_PLANO,
)

from historico import Historico


class Inteligencia:

    def __init__(self):
        self.historico = Historico()

        self.instrucoes = (
            "Você é ALBERTO, um assistente pessoal inteligente que "
            "conversa em português brasileiro. "
            "Compreenda a intenção do usuário, não apenas as palavras "
            "utilizadas. Considere o contexto da conversa. "
            "Seja natural, preciso e objetivo. "
            "Não invente informações nem afirme que realizou ações "
            "sem receber confirmação real."
        )

    def _consultar(
        self,
        mensagens,
        formato=None,
        timeout=None,
        max_tokens=None
    ):
        payload = {
            "model": OLLAMA_MODELO,
            "messages": mensagens,
            "stream": False,
            "keep_alive": OLLAMA_KEEP_ALIVE,
            "options": {
                "temperature": 0.2,
                "num_ctx": OLLAMA_NUM_CTX,
                "num_predict": (
                    max_tokens
                    if max_tokens is not None
                    else OLLAMA_MAX_TOKENS_RESPOSTA
                ),
                "num_thread": OLLAMA_NUM_THREAD
            }
        }

        if formato:
            payload["format"] = formato

        dados = json.dumps(
            payload,
            ensure_ascii=False
        ).encode("utf-8")

        requisicao = urllib.request.Request(
            OLLAMA_URL,
            data=dados,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        with urllib.request.urlopen(
            requisicao,
            timeout=timeout or TIMEOUT_OLLAMA
        ) as resposta:

            resultado = json.loads(
                resposta.read().decode("utf-8")
            )

        return resultado.get(
            "message", {}
        ).get("content", "").strip()

    def perguntar(self, pergunta):
        pergunta = str(pergunta).strip()

        if not pergunta:
            return "Não recebi uma pergunta."

        mensagens = [
            {
                "role": "system",
                "content": self.instrucoes
            }
        ]

        mensagens.extend(
            self.historico.obter(
                limite=8,
                max_caracteres=5000
            )
        )

        mensagens.append({
            "role": "user",
            "content": pergunta
        })

        try:
            texto = self._consultar(
                mensagens,
                max_tokens=OLLAMA_MAX_TOKENS_RESPOSTA
            )

            if not texto:
                return "Não consegui formular uma resposta."

            self.historico.adicionar("user", pergunta)
            self.historico.adicionar("assistant", texto)

            return texto

        except urllib.error.HTTPError as erro:
            return f"O Ollama retornou um erro HTTP: {erro.code}."

        except urllib.error.URLError:
            return (
                "Não consegui conectar ao Ollama. "
                "Verifique se o servidor está funcionando."
            )

        except Exception as erro:
            return (
                "Erro na inteligência local: "
                f"{type(erro).__name__}: {erro}"
            )

    def planejar(self, pedido, ferramentas):
        sistema = (
            "Você é o cérebro de planejamento do ALBERTO. "
            "Interprete a intenção real do usuário considerando "
            "o histórico e as ferramentas disponíveis.\n\n"

            "Retorne somente JSON válido em um destes formatos:\n"
            '{"tipo":"responder","resposta":"texto"}\n'
            '{"tipo":"esclarecer","pergunta":"texto"}\n'
            '{"tipo":"executar","acoes":['
            '{"ferramenta":"nome","argumentos":{}}]}\n\n'

            "FERRAMENTAS E ESQUEMAS:\n"
            + json.dumps(ferramentas, ensure_ascii=False)
            + "\n\n"

            "REGRAS:\n"
            "1. Use somente ferramentas disponíveis.\n"
            "2. Respeite exatamente os nomes e tipos dos argumentos.\n"
            "3. Nunca use o nome de um campo como valor.\n"
            "4. Não invente informações, arquivos ou coordenadas.\n"
            "5. Se faltar informação essencial, pergunte.\n"
            "6. Perguntas devem receber respostas, não ações.\n"
            "7. Ordens devem gerar ações quando houver ferramenta adequada.\n"
            "8. Interprete pedidos com várias etapas na ordem solicitada.\n"
            "9. Não utilize comandos arbitrários, shell, exec ou eval.\n"
            "10. Não afirme que uma ação foi executada.\n"
            "11. Use no máximo 4 ações por solicitação.\n"
            "12. Considere referências ao contexto anterior.\n"
            "13. Responda sempre em português brasileiro."
        )

        mensagens = [
            {
                "role": "system",
                "content": sistema
            }
        ]

        mensagens.extend(
            self.historico.obter(
                limite=8,
                max_caracteres=5000
            )
        )

        mensagens.append({
            "role": "user",
            "content": str(pedido)[:2000]
        })

        try:
            bruto = self._consultar(
                mensagens,
                formato="json",
                max_tokens=OLLAMA_MAX_TOKENS_PLANO
            )

            plano = json.loads(bruto)

            if not isinstance(plano, dict):
                return None

            tipo = plano.get("tipo")

            if tipo == "responder":
                resposta = plano.get("resposta")

                if isinstance(resposta, str) and resposta.strip():
                    return plano

            elif tipo == "esclarecer":
                pergunta = plano.get("pergunta")

                if isinstance(pergunta, str) and pergunta.strip():
                    return plano

            elif tipo == "executar":
                acoes = plano.get("acoes")

                if (
                    isinstance(acoes, list)
                    and 1 <= len(acoes) <= 4
                    and all(isinstance(a, dict) for a in acoes)
                ):
                    return plano

            return None

        except (
            json.JSONDecodeError,
            urllib.error.URLError,
            urllib.error.HTTPError,
            TimeoutError,
            OSError,
            TypeError,
            ValueError
        ):
            return None

        except Exception:
            return None

    def resumir_execucao(self, pedido, resultados):
        """
        Mantido para compatibilidade com módulos antigos.
        Não realiza uma consulta adicional ao Ollama.
        """

        linhas = [
            f"{i}. {resultado}"
            for i, resultado in enumerate(resultados, 1)
        ]

        resposta = "\n".join(linhas)

        self.historico.adicionar("user", pedido)
        self.historico.adicionar("assistant", resposta)

        return resposta