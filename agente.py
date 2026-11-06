import json
from datetime import datetime


class Agente:
    MAX_ACOES = 4
    MAX_TEXTO = 500

    def __init__(
        self, ia, seguranca, sistema, memoria,
        mouse, teclado, janelas, processos, navegador
    ):
        self.ia = ia
        self.seguranca = seguranca
        self.sistema = sistema
        self.memoria = memoria
        self.mouse = mouse
        self.teclado = teclado
        self.janelas = janelas
        self.processos = processos
        self.navegador = navegador

        self.ferramentas = {
            "horario_atual": (
                "Informa data e horário local do computador.",
                {},
                lambda a: datetime.now().strftime(
                    "São %H:%M de %d/%m/%Y."
                )
            ),

            "abrir_aplicativo": (
                "Abre um aplicativo encontrado no Menu Iniciar ou PATH.",
                {"nome": "string"},
                self._abrir_app
            ),

            "listar_aplicativos": (
                "Lista aplicativos encontrados nos atalhos do Menu Iniciar.",
                {},
                lambda a: self._listar_aplicativos()
            ),

            "abrir_site": (
                "Abre um endereço HTTPS no navegador.",
                {"endereco": "string"},
                self._abrir_site
            ),

            "pesquisar_web": (
                "Pesquisa um assunto na web usando Google.",
                {"consulta": "string"},
                self._pesquisar
            ),

            "listar_arquivos": (
                "Lista arquivos dentro da pasta workspace.",
                {},
                lambda a: self._listar_arquivos()
            ),

            "ler_arquivo": (
                "Lê um arquivo de texto dentro da workspace.",
                {"nome": "string"},
                lambda a: self._ler_arquivo(a)
            ),

            "criar_arquivo": (
                "Cria um arquivo novo dentro da workspace; nunca sobrescreve.",
                {"nome": "string", "conteudo": "string"},
                lambda a: self._criar_arquivo(a)
            ),

            "informacoes_sistema": (
                "Consulta informações de hardware e sistema.",
                {},
                lambda a: self.sistema.resumo()
            ),

            "listar_janelas": (
                "Lista títulos das janelas abertas.",
                {},
                lambda a: self.janelas.listar_janelas()
            ),

            "janela_ativa": (
                "Informa qual janela está ativa.",
                {},
                lambda a: self.janelas.obter_janela_ativa()
            ),

            "ativar_janela": (
                "Traz uma janela para primeiro plano.",
                {"trecho_titulo": "string"},
                lambda a: self.janelas.ativar(a["trecho_titulo"])
            ),

            "minimizar_janela": (
                "Minimiza uma janela.",
                {"trecho_titulo": "string"},
                lambda a: self.janelas.minimizar(a["trecho_titulo"])
            ),

            "maximizar_janela": (
                "Maximiza uma janela.",
                {"trecho_titulo": "string"},
                lambda a: self.janelas.maximizar(a["trecho_titulo"])
            ),

            "posicao_mouse": (
                "Consulta a posição atual do mouse.",
                {},
                lambda a: self.mouse.obter_posicao()
            ),

            "mover_mouse": (
                "Move o mouse para coordenadas da tela.",
                {"x": "integer", "y": "integer"},
                lambda a: self.mouse.mover(a["x"], a["y"])
            ),

            "clicar_mouse": (
                "Clica na posição atual ou nas coordenadas informadas.",
                {
                    "x": "integer|null",
                    "y": "integer|null",
                    "botao": "left|right|middle"
                },
                self._clicar
            ),

            "rolar_tela": (
                "Rola a página.",
                {"quantidade": "integer"},
                lambda a: self.mouse.rolar(a["quantidade"])
            ),

            "digitar_texto": (
                "Digita texto no aplicativo ativo.",
                {"texto": "string"},
                lambda a: self.teclado.digitar_texto(a["texto"])
            ),

            "pressionar_tecla": (
                "Pressiona uma tecla permitida.",
                {"tecla": "string"},
                lambda a: self.teclado.pressionar_tecla(a["tecla"])
            ),

            "executar_atalho": (
                "Executa um atalho permitido.",
                {"atalho": "string"},
                lambda a: self.teclado.executar_atalho(a["atalho"])
            ),

            "listar_processos": (
                "Lista processos em execução sem modificá-los.",
                {},
                lambda a: self.processos.listar()
            ),

            "pesquisar_processo": (
                "Procura processos pelo nome.",
                {"termo": "string"},
                lambda a: self.processos.pesquisar(a["termo"])
            ),

            "salvar_memoria": (
                "Salva uma nota explicitamente solicitada pelo usuário.",
                {"nota": "string"},
                lambda a: self.memoria.adicionar(a["nota"])
            ),

            "listar_memoria": (
                "Lista notas salvas pelo usuário.",
                {},
                lambda a: self.memoria.listar()
            )
        }

    # --------------------------------------------------
    # FERRAMENTAS
    # --------------------------------------------------

    def _abrir_app(self, a):
        from automacao import abrir_aplicativo
        return abrir_aplicativo(a["nome"], self.seguranca)

    def _listar_aplicativos(self):
        from automacao import listar_aplicativos_instalados
        return listar_aplicativos_instalados()

    def _abrir_site(self, a):
        return self.navegador.abrir_site(
            a["endereco"], self.seguranca
        )

    def _pesquisar(self, a):
        from automacao import pesquisar_google
        return pesquisar_google(a["consulta"])

    def _listar_arquivos(self):
        from arquivos import listar_arquivos
        return listar_arquivos()

    def _ler_arquivo(self, a):
        from arquivos import ler_arquivo
        return ler_arquivo(a["nome"])

    def _criar_arquivo(self, a):
        from arquivos import criar_arquivo
        return criar_arquivo(
            a["nome"],
            a["conteudo"],
            self.seguranca
        )

    def _clicar(self, a):
        x = a.get("x")
        y = a.get("y")

        if (x is None) != (y is None):
            return (
                "Informe x e y juntos, ou deixe ambos vazios "
                "para clicar na posição atual."
            )

        return self.mouse.clicar(
            x, y, a.get("botao", "left")
        )

    # --------------------------------------------------
    # DESCRIÇÃO DAS FERRAMENTAS
    # --------------------------------------------------

    def _descricao_ferramentas(self):
        return {
            nome: {
                "descricao": info[0],
                "argumentos": info[1]
            }
            for nome, info in self.ferramentas.items()
        }

    # --------------------------------------------------
    # VALIDAÇÃO
    # --------------------------------------------------

    def _validar_argumentos(self, ferramenta, argumentos):

        if ferramenta not in self.ferramentas:
            return False, "Ferramenta inexistente."

        if not isinstance(argumentos, dict):
            return False, "Os argumentos precisam ser um objeto."

        esquema = self.ferramentas[ferramenta][1]

        obrigatorios = {
            chave
            for chave, tipo in esquema.items()
            if not tipo.endswith("|null")
        }

        permitidos = set(esquema)

        faltando = obrigatorios - set(argumentos)
        extras = set(argumentos) - permitidos

        if faltando:
            return False, (
                "Argumentos obrigatórios ausentes: "
                + ", ".join(sorted(faltando))
            )

        if extras:
            return False, (
                "Argumentos desconhecidos: "
                + ", ".join(sorted(extras))
            )

        for chave, valor in argumentos.items():

            tipo = esquema[chave]

            if tipo == "string":

                if not isinstance(valor, str):
                    return False, f"{chave} precisa ser texto."

                if not valor.strip():
                    return False, f"{chave} não pode estar vazio."

                if valor.strip().casefold() == chave.casefold():
                    return False, (
                        f"{chave} recebeu o nome do campo "
                        "em vez do valor."
                    )

                if len(valor) > self.MAX_TEXTO:
                    return False, f"{chave} excede o limite permitido."

            elif tipo == "integer":

                if isinstance(valor, bool) or not isinstance(valor, int):
                    return False, f"{chave} precisa ser inteiro."

            elif tipo == "integer|null":

                if valor is not None:
                    if isinstance(valor, bool) or not isinstance(valor, int):
                        return False, f"{chave} precisa ser inteiro ou nulo."

            elif tipo == "left|right|middle":

                if valor not in {"left", "right", "middle"}:
                    return False, "Botão do mouse inválido."

        if ferramenta == "clicar_mouse":

            x = argumentos.get("x")
            y = argumentos.get("y")

            if (x is None) != (y is None):
                return False, "As coordenadas x e y devem ser informadas juntas."

        if ferramenta in {"mover_mouse", "clicar_mouse"}:

            for eixo in ("x", "y"):
                valor = argumentos.get(eixo)

                if valor is not None and not 0 <= valor <= 10000:
                    return False, f"Coordenada {eixo} fora do limite."

        if ferramenta == "rolar_tela":

            if not -10 <= argumentos["quantidade"] <= 10:
                return False, "A rolagem deve ficar entre -10 e 10."

        if ferramenta == "digitar_texto":

            if len(argumentos["texto"]) > self.MAX_TEXTO:
                return False, "O texto excede 500 caracteres."

        return True, ""

    def _validar_plano(self, acoes):

        if not isinstance(acoes, list) or not acoes:
            return False, "O plano não contém ações válidas."

        if len(acoes) > self.MAX_ACOES:
            return False, (
                f"O plano excedeu o limite de "
                f"{self.MAX_ACOES} ações."
            )

        # Todas as ações são verificadas antes da primeira execução.
        for indice, acao in enumerate(acoes, 1):

            if not isinstance(acao, dict):
                return False, f"A ação {indice} está malformada."

            nome = acao.get("ferramenta")
            argumentos = acao.get("argumentos", {})

            if nome not in self.ferramentas:
                return False, f"Ferramenta desconhecida na ação {indice}."

            valido, motivo = self._validar_argumentos(
                nome, argumentos
            )

            if not valido:
                return False, f"Ação {indice}: {motivo}"

        return True, ""

    # --------------------------------------------------
    # HISTÓRICO E DIAGNÓSTICO
    # --------------------------------------------------

    def _registrar_conversa(self, pedido, resposta):

        self.ia.historico.adicionar("user", pedido)
        self.ia.historico.adicionar("assistant", resposta)

    def _registrar_diagnostico(self, evento):

        try:
            from configuracoes import PASTA_LOGS

            PASTA_LOGS.mkdir(parents=True, exist_ok=True)

            caminho = PASTA_LOGS / "diagnostico_agente.jsonl"

            registro = {
                "momento": datetime.now().isoformat(
                    timespec="seconds"
                ),
                **evento
            }

            with caminho.open("a", encoding="utf-8") as arquivo:
                arquivo.write(
                    json.dumps(
                        registro,
                        ensure_ascii=False,
                        default=str
                    ) + "\n"
                )

        except Exception:
            pass

    # --------------------------------------------------
    # CONTROLE DE COMANDOS
    # --------------------------------------------------

    def _comando_especial(self, texto):

        comando = " ".join(
            texto.casefold()
            .replace(",", " ")
            .strip()
            .rstrip(".!?")
            .split()
        )

        if comando in {
            "sair",
            "encerrar",
            "desligar alberto",
            "fechar alberto"
        }:
            return "__ENCERRAR__"

        if comando in {
            "cancelar",
            "cancela",
            "alberto cancelar",
            "pare",
            "parar",
            "interromper",
            "alberto pare"
        }:
            return "__CANCELAR__"

        return None

    # --------------------------------------------------
    # EXECUÇÃO
    # --------------------------------------------------

    def processar(self, texto):

        texto = str(texto).strip()

        if not texto:
            return "Não recebi nenhuma instrução."

        especial = self._comando_especial(texto)

        if especial:
            return especial

        # Uma única chamada para interpretar a solicitação.
        plano = self.ia.planejar(
            texto,
            self._descricao_ferramentas()
        )

        if not isinstance(plano, dict):
            resposta = self.ia.perguntar(texto)
            return resposta

        tipo = plano.get("tipo")

        # Perguntas e conversas.
        if tipo == "responder":

            resposta = plano["resposta"].strip()

            self._registrar_conversa(texto, resposta)

            return resposta

        # Solicitação de esclarecimento.
        if tipo == "esclarecer":

            resposta = plano["pergunta"].strip()

            self._registrar_conversa(texto, resposta)

            return resposta

        if tipo != "executar":
            return (
                "Não consegui identificar sua intenção. "
                "Pode explicar de outra maneira?"
            )

        acoes = plano.get("acoes")

        # Valida o plano inteiro antes de executar.
        valido, motivo = self._validar_plano(acoes)

        if not valido:

            self._registrar_diagnostico({
                "pedido": texto,
                "plano": plano,
                "bloqueado": motivo
            })

            return (
                "Não executei nenhuma ação porque o plano "
                "apresentou um problema: " + motivo
            )

        self._registrar_diagnostico({
            "pedido": texto,
            "plano": plano
        })

        resultados = []

        for indice, acao in enumerate(acoes, 1):

            nome = acao["ferramenta"]
            argumentos = acao.get("argumentos", {})

            try:

                resultado = self.ferramentas[nome][2](argumentos)

                if resultado is None:
                    resultado = "A ferramenta não retornou informações."

            except (KeyError, TypeError, ValueError) as erro:

                resultado = (
                    f"Argumentos inválidos para {nome}: {erro}"
                )

            except Exception as erro:

                self.seguranca.registrar_erro(erro)

                resultado = (
                    f"A ferramenta {nome} falhou: "
                    f"{type(erro).__name__}."
                )

            resultado = str(resultado)

            resultados.append((nome, resultado))

            self._registrar_diagnostico({
                "acao": indice,
                "ferramenta": nome,
                "argumentos": argumentos,
                "resultado": resultado
            })

            # Interrompe a sequência se uma etapa falhar.
            indicadores_falha = (
                "não consegui",
                "não encontrei",
                "inválid",
                "bloquead",
                "falhou",
                "cancelad",
                "erro:"
            )

            if any(
                palavra in resultado.casefold()
                for palavra in indicadores_falha
            ):
                break

        if not resultados:
            return "Nenhuma ação foi executada."

        linhas = [
            f"{indice}. {nome}: {resultado}"
            for indice, (nome, resultado)
            in enumerate(resultados, 1)
        ]

        resumo = "\n".join(linhas)

        # Usa o método existente sem exigir outra consulta à IA.
        resposta = self.ia.resumir_execucao(
            texto,
            resumo.splitlines()
        )

        return resposta or resumo

