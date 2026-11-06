def processar_comando(instrucao, voz, ia, seguranca=None, sistema=None, memoria=None,
                      mouse=None, teclado=None, janelas=None, processos=None,
                      internet=None, navegador=None, agente=None):
    """Mantém a interface antiga, mas delega a interpretação ao planejador inteligente."""
    texto = str(instrucao).strip()
    if not texto:
        return "Não entendi o que você disse."
    if texto.casefold() in {"sair", "encerrar", "desligar alberto", "fechar alberto"}:
        return "__ENCERRAR__"
    if agente is not None:
        return agente.processar(texto)
    return ia.perguntar(texto)
