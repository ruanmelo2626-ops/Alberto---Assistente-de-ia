import unittest
from agente import Agente

class FalsoHistorico:
    def __init__(self): self.itens = []
    def adicionar(self, papel, conteudo): self.itens.append((papel, conteudo))

class FalsaIA:
    def __init__(self, plano): self.plano = plano; self.historico = FalsoHistorico(); self.pedido = None
    def planejar(self, pedido, ferramentas): self.pedido = pedido; return self.plano
    def perguntar(self, pergunta): return "Resposta simulada."
    def resumir_execucao(self, pedido, resultados): return " | ".join(resultados)

class FalsoSeguranca:
    def registrar_erro(self, erro): pass

class FalsoSistema:
    def resumo(self): return "Sistema OK"
class FalsoMemoria:
    def adicionar(self, nota): return "Nota salva"
    def listar(self): return "Memória"
class FalsoMouse:
    def obter_posicao(self): return "X=1 Y=2"
class FalsoTeclado: pass
class FalsoJanelas:
    def listar_janelas(self): return "Janela A"
    def obter_janela_ativa(self): return "Janela A"
class FalsoProcessos:
    def listar(self): return "Processos"
    def pesquisar(self, termo): return termo
class FalsoNavegador: pass

class TesteAgente(unittest.TestCase):
    def criar(self, plano):
        ia = FalsaIA(plano)
        agente = Agente(ia, FalsoSeguranca(), FalsoSistema(), FalsoMemoria(), FalsoMouse(),
                        FalsoTeclado(), FalsoJanelas(), FalsoProcessos(), FalsoNavegador())
        return agente, ia

    def test_resposta_sem_acao(self):
        agente, _ = self.criar({"tipo":"responder", "resposta":"Olá!"})
        self.assertEqual(agente.processar("oi"), "Olá!")

    def test_ferramenta_desconhecida_bloqueada(self):
        agente, _ = self.criar({"tipo":"executar", "acoes":[{"ferramenta":"shell", "argumentos":{}}]})
        self.assertIn("bloqueado", agente.processar("faça algo").lower())

    def test_limite_de_acoes(self):
        agente, _ = self.criar({"tipo":"executar", "acoes":[{"ferramenta":"listar_janelas", "argumentos":{}}]*5})
        self.assertIn("limite", agente.processar("faça várias coisas").lower())

    def test_encerra(self):
        agente, _ = self.criar(None)
        self.assertEqual(agente.processar("encerrar"), "__ENCERRAR__")

    def test_cancelar_por_comando(self):
        agente, _ = self.criar(None)
        self.assertEqual(agente.processar("Alberto, cancelar!"), "__CANCELAR__")

    def test_multiplas_acoes_em_ordem(self):
        plano = {"tipo": "executar", "acoes": [
            {"ferramenta": "horario_atual", "argumentos": {}},
            {"ferramenta": "listar_janelas", "argumentos": {}}
        ]}
        agente, _ = self.criar(plano)
        resposta = agente.processar("Que horas são e liste as janelas")
        self.assertIn("1. horario_atual:", resposta)
        self.assertIn("2. listar_janelas:", resposta)
        self.assertLess(resposta.index("horario_atual"), resposta.index("listar_janelas"))

if __name__ == "__main__":
    unittest.main(verbosity=2)
