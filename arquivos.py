from configuracoes import PASTA_TRABALHO, LIMITE_TEXTO_ARQUIVO
from seguranca import Seguranca

def _destino(nome):
    if not isinstance(nome, str) or not nome.strip():
        raise ValueError("Informe um nome de arquivo válido.")
    return Seguranca().validar_caminho(nome.strip())

def criar_arquivo(nome, conteudo="", seguranca=None):
    destino = _destino(nome)
    if not isinstance(conteudo, str):
        return "O conteúdo precisa ser texto."
    if len(conteudo) > 100000:
        return "O conteúdo excede o limite de 100.000 caracteres."
    if destino.exists():
        return "Esse arquivo já existe. Não alterei seu conteúdo."
    if seguranca and not seguranca.confirmar_acao(f"criar o arquivo {destino.name}"):
        return "Criação cancelada."
    try:
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(conteudo, encoding="utf-8")
    except OSError as erro:
        return f"Não consegui criar o arquivo: {erro}"
    if seguranca:
        seguranca.registrar(f"Arquivo criado: {destino}")
    return f"Arquivo criado: {destino}"

def ler_arquivo(nome):
    destino = _destino(nome)
    if not destino.is_file():
        return "Não encontrei esse arquivo na pasta workspace."
    if destino.stat().st_size > 1_000_000:
        return "Arquivo muito grande para leitura por voz."
    return destino.read_text(encoding="utf-8", errors="replace")[:LIMITE_TEXTO_ARQUIVO]

def listar_arquivos():
    PASTA_TRABALHO.mkdir(parents=True, exist_ok=True)
    itens = []
    for item in PASTA_TRABALHO.rglob("*"):
        if item.is_file() and "logs" not in item.parts and "__pycache__" not in item.parts:
            itens.append(str(item.relative_to(PASTA_TRABALHO)))
    return "\n".join(itens[:100]) if itens else "A pasta workspace está vazia."
