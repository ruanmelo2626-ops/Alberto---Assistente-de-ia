"""Agente de execução do ALBERTO: linguagem natural -> plano validado -> ferramentas."""
import json
from datetime import datetime

class Agente:
    MAX_ACOES = 4

    def __init__(self, ia, seguranca, sistema, memoria, mouse, teclado, janelas, processos, navegador):
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
            "horario_atual": ("Informa data e horário local do computador.", {}, lambda a: datetime.now().strftime("São %H:%M de %d/%m/%Y.")),
            "abrir_aplicativo": ("Abre um aplicativo encontrado no Menu Iniciar ou PATH.", {"nome": "string"}, self._abrir_app),
            "listar_aplicativos": ("Lista aplicativos encontrados nos atalhos do Menu Iniciar.", {}, lambda a: self._listar_aplicativos()),
            "abrir_site": ("Abre um endereço HTTPS no navegador.", {"endereco": "string"}, self._abrir_site),
            "pesquisar_web": ("Pesquisa um assunto na web usando Google.", {"consulta": "string"}, self._pesquisar),
            "listar_arquivos": ("Lista arquivos dentro da pasta workspace.", {}, lambda a: self._listar_arquivos()),
            "ler_arquivo": ("Lê um arquivo de texto dentro da workspace.", {"nome": "string"}, lambda a: self._ler_arquivo(a)),
            "criar_arquivo": ("Cria um arquivo novo dentro da workspace; nunca sobrescreve.", {"nome": "string", "conteudo": "string"}, lambda a: self._criar_arquivo(a)),
            "informacoes_sistema": ("Consulta informações de hardware e sistema.", {}, lambda a: self.sistema.resumo()),
            "listar_janelas": ("Lista títulos das janelas abertas.", {}, lambda a: self.janelas.listar_janelas()),
            "janela_ativa": ("Informa qual janela está ativa.", {}, lambda a: self.janelas.obter_janela_ativa()),
            "ativar_janela": ("Traz uma janela para primeiro plano; requer confirmação.", {"trecho_titulo": "string"}, lambda a: self.janelas.ativar(a["trecho_titulo"])),
            "minimizar_janela": ("Minimiza uma janela; requer confirmação.", {"trecho_titulo": "string"}, lambda a: self.janelas.minimizar(a["trecho_titulo"])),
            "maximizar_janela": ("Maximiza uma janela; requer confirmação.", {"trecho_titulo": "string"}, lambda a: self.janelas.maximizar(a["trecho_titulo"])),
            "posicao_mouse": ("Consulta a posição atual do mouse.", {}, lambda a: self.mouse.obter_posicao()),
            "mover_mouse": ("Move o mouse para coordenadas da tela; requer confirmação.", {"x": "integer", "y": "integer"}, lambda a: self.mouse.mover(a["x"], a["y"])),
            "clicar_mouse": ("Clica na posição atual ou nas coordenadas informadas; requer confirmação.", {"x": "integer|null", "y": "integer|null", "botao": "left|right|middle"}, self._clicar),
            "rolar_tela": ("Rola a página; requer confirmação.", {"quantidade": "integer"}, lambda a: self.mouse.rolar(a["quantidade"])),
            "digitar_texto": ("Digita texto no aplicativo ativo; requer confirmação.", {"texto": "string"}, lambda a: self.teclado.digitar_texto(a["texto"])),
            "pressionar_tecla": ("Pressiona uma tecla permitida; requer confirmação.", {"tecla": "string"}, lambda a: self.teclado.pressionar_tecla(a["tecla"])),
            "executar_atalho": ("Executa um atalho permitido; requer confirmação.", {"atalho": "string"}, lambda a: self.teclado.executar_atalho(a["atalho"])),
            "listar_processos": ("Lista processos em execução sem modificá-los.", {}, lambda a: self.processos.listar()),
            "pesquisar_processo": ("Procura processos pelo nome.", {"termo": "string"}, lambda a: self.processos.pesquisar(a["termo"])),
            "salvar_memoria": ("Salva uma nota explicitamente solicitada pelo usuário.", {"nota": "string"}, lambda a: self.memoria.adicionar(a["nota"])),
            "listar_memoria": ("Lista notas salvas pelo usuário.", {}, lambda a: self.memoria.listar()),
        }

    def _abrir_app(self, a):
        from automacao import abrir_aplicativo
        return abrir_aplicativo(a["nome"], self.seguranca)

    def _listar_aplicativos(self):
        from automacao import listar_aplicativos_instalados
        return listar_aplicativos_instalados()

    def _abrir_site(self, a):
        return self.navegador.abrir_site(a["endereco"], self.seguranca)

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
        return criar_arquivo(a["nome"], a["conteudo"], self.seguranca)

    def _clicar(self, a):
        x, y = a.get("x"), a.get("y")
        if (x is None) != (y is None):
            return "Informe x e y juntos, ou deixe ambos vazios para clicar na posição atual."
        return self.mouse.clicar(x, y, a.get("botao", "left"))

    def _descricao_ferramentas(self):
        return {nome: {"descricao": info[0], "argumentos": info[1]} for nome, info in self.ferramentas.items()}

    def _validar_argumentos(self, ferramenta, argumentos):
        """Valida argumentos antes de chamar qualquer ferramenta."""
        if ferramenta not in self.ferramentas or not isinstance(argumentos, dict):
            return False, "Ferramenta ou objeto de argumentos inválido."
        esquema = self.ferramentas[ferramenta][1]
        obrigatorios = {k for k, tipo in esquema.items() if not str(tipo).endswith("|null")}
        permitidos = set(esquema)
        faltando = obrigatorios - set(argumentos)
        extras = set(argumentos) - permitidos
        if faltando:
            return False, "Faltam os argumentos obrigatórios: " + ", ".join(sorted(faltando))
        if extras:
            return False, "Argumentos não reconhecidos: " + ", ".join(sorted(extras))
        for chave, valor in argumentos.items():
            tipo = esquema[chave]
            if tipo == "string":
                if not isinstance(valor, str) or not valor.strip():
                    return False, f"O argumento {chave} precisa ser um texto válido."
                if valor.strip().casefold() == chave.casefold():
                    return False, f"O argumento {chave} recebeu o nome do campo em vez do valor."
                if len(valor) > 500:
                    return False, f"O argumento {chave} excede o limite permitido."
            elif tipo == "integer|null":
                if valor is not None and (isinstance(valor, bool) or not isinstance(valor, int)):
                    return False, f"O argumento {chave} precisa ser um número inteiro ou nulo."
            elif tipo == "integer":
                if isinstance(valor, bool) or not isinstance(valor, int):
                    return False, f"O argumento {chave} precisa ser um número inteiro."
            elif tipo == "left|right|middle":
                if valor not in {"left", "right", "middle"}:
                    return False, "Botão do mouse inválido."
        if ferramenta in {"mover_mouse", "clicar_mouse"}:
            for eixo in ("x", "y"):
                valor = argumentos.get(eixo)
                if valor is not None and not 0 <= valor <= 10000:
                    return False, f"Coordenada {eixo} fora do limite permitido."
        if ferramenta == "rolar_tela" and not -10 <= argumentos["quantidade"] <= 10:
            return False, "A rolagem deve ficar entre -10 e 10."
        if ferramenta == "digitar_texto" and len(argumentos["texto"]) > 500:
            return False, "O texto excede 500 caracteres."
        return True, ""

    def processar(self, texto):
        texto = str(texto).strip()
        if not texto:
            return "Não recebi nenhuma instrução."
        comando = " ".join(texto.casefold().replace(",", " ").strip().rstrip(".!?").split())
        if comando in {"sair", "encerrar", "desligar alberto", "fechar alberto"}:
            return "__ENCERRAR__"
        if comando in {"cancelar", "cancela", "alberto cancelar", "pare", "parar", "interromper", "alberto pare"}:
            return "__CANCELAR__"
        plano = self.ia.planejar(texto, self._descricao_ferramentas())
        if not isinstance(plano, dict):
            return self.ia.perguntar(texto)
        tipo = plano.get("tipo")
        if tipo == "responder":
            resposta = str(plano.get("resposta", "" )).strip()
            resposta = resposta or "Não consegui formular uma resposta."
            self.ia.historico.adicionar("user", texto)
            self.ia.historico.adicionar("assistant", resposta)
            return resposta
        if tipo == "esclarecer":
            resposta = str(plano.get("pergunta", "Pode explicar melhor o que deseja?")).strip()
            self.ia.historico.adicionar("user", texto)
            self.ia.historico.adicionar("assistant", resposta)
            return resposta
        if tipo != "executar":
            return "Não consegui identificar se você queria uma resposta ou uma ação. Pode reformular?"
        acoes = plano.get("acoes")
        if not isinstance(acoes, list) or not acoes:
            return "O plano não contém ações válidas."
        if len(acoes) > self.MAX_ACOES:
            return f"O plano excedeu o limite de {self.MAX_ACOES} ações por solicitação. Divida a tarefa em etapas."
        resultados = []
        self._registrar_diagnostico({"pedido": texto, "plano": plano})
        for indice, acao in enumerate(acoes, 1):
            if not isinstance(acao, dict):
                return "Plano inválido: uma ação está malformada."
            nome, args = acao.get("ferramenta"), acao.get("argumentos", {})
            if nome not in self.ferramentas or not isinstance(args, dict):
                return f"Plano bloqueado: ferramenta ou argumentos inválidos ({nome})."
            valido, motivo = self._validar_argumentos(nome, args)
            if not valido:
                # Uma única tentativa de correção pelo modelo, sem executar o plano inválido.
                correcao = (
                    texto + "\n\nCORRIJA O PLANO ANTERIOR. A validação rejeitou a ferramenta "
                    + str(nome) + ". Motivo: " + motivo
                    + ". Gere novamente um JSON completo, com valores reais nos argumentos; "
                    "não use o nome do campo como valor. Se não souber o valor, peça esclarecimento."
                )
                novo_plano = self.ia.planejar(correcao, self._descricao_ferramentas())
                if isinstance(novo_plano, dict) and novo_plano.get("tipo") == "executar":
                    novas_acoes = novo_plano.get("acoes")
                    if isinstance(novas_acoes, list) and len(novas_acoes) == 1 and isinstance(novas_acoes[0], dict):
                        nome = novas_acoes[0].get("ferramenta")
                        args = novas_acoes[0].get("argumentos", {})
                        valido, motivo = self._validar_argumentos(nome, args)
                if not valido:
                    return ("Não executei a ação porque o planejador produziu argumentos incorretos. "
                            f"Detalhe: {motivo} Tente explicar o pedido de outra forma.")
            try:
                resultado = self.ferramentas[nome][2](args)
            except (KeyError, TypeError, ValueError) as erro:
                resultado = f"Argumentos inválidos para {nome}: {erro}"
            except Exception as erro:
                self.seguranca.registrar_erro(erro)
                resultado = f"A ferramenta {nome} falhou: {type(erro).__name__}."
            resultados.append((nome, str(resultado)))
            self._registrar_diagnostico({"acao": indice, "ferramenta": nome, "argumentos": args, "resultado": str(resultado)})
            if any(p in str(resultado).casefold() for p in ("cancelad", "não consegui", "não encontrei", "inválid", "bloquead", "erro")):
                break
        linhas = [f"{i}. {nome}: {resultado}" for i, (nome, resultado) in enumerate(resultados, 1)]
        if not linhas:
            return "Nenhuma ação foi executada."
        return "Concluído.\n" + "\n".join(linhas)

    def _registrar_diagnostico(self, evento):
        try:
            from configuracoes import PASTA_LOGS
            PASTA_LOGS.mkdir(parents=True, exist_ok=True)
            caminho = PASTA_LOGS / "diagnostico_agente.jsonl"
            with caminho.open("a", encoding="utf-8") as arquivo:
                arquivo.write(json.dumps({"momento": datetime.now().isoformat(timespec="seconds"), **evento}, ensure_ascii=False, default=str) + "\n")
        except Exception:
            pass
