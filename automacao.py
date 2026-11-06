import os
import shutil
import subprocess
import webbrowser
from pathlib import Path
from urllib.parse import quote_plus
import unicodedata

APLICATIVOS_PERMITIDOS = {
    "bloco de notas": ["notepad.exe"],
    "notepad": ["notepad.exe"],
    "calculadora": ["calc.exe"],
    "explorador de arquivos": ["explorer.exe"],
    "explorador": ["explorer.exe"],
    "paint": ["mspaint.exe"],
    "visual studio code": ["code"],
    "vscode": ["code"],
}


def _normalizar(texto):
    texto = unicodedata.normalize("NFD", str(texto).casefold())
    return "".join(
        c for c in texto
        if unicodedata.category(c) != "Mn"
    ).strip()


def _atalhos_menu_iniciar():
    """Encontra atalhos instalados nos menus Iniciar."""
    pastas = [
        Path(os.environ.get("APPDATA", ""))
        / "Microsoft/Windows/Start Menu/Programs",

        Path(os.environ.get("PROGRAMDATA", ""))
        / "Microsoft/Windows/Start Menu/Programs",
    ]

    for pasta in pastas:
        if not pasta.is_dir():
            continue

        try:
            for atalho in pasta.rglob("*.lnk"):
                yield atalho
        except OSError:
            continue


def listar_aplicativos_instalados(limite=80):
    nomes = sorted(
        {atalho.stem for atalho in _atalhos_menu_iniciar()},
        key=str.casefold
    )

    limite = max(1, min(int(limite), 150))

    return "\n".join(nomes[:limite]) or (
        "Não encontrei atalhos no Menu Iniciar."
    )


def _localizar_aplicativo(nome):
    chave = _normalizar(nome)

    if not chave:
        return None

    # Primeiro: aliases conhecidos.
    comando = APLICATIVOS_PERMITIDOS.get(chave)

    if comando:
        return ("comando", comando)

    # Segundo: procurar no PATH.
    executavel = shutil.which(nome.strip())

    if executavel:
        return ("comando", [executavel])

    # Terceiro: procurar atalhos no Menu Iniciar.
    correspondencias = []

    for atalho in _atalhos_menu_iniciar():
        nome_atalho = _normalizar(atalho.stem)

        if chave == nome_atalho:
            return ("atalho", atalho)

        if chave in nome_atalho or nome_atalho in chave:
            correspondencias.append(atalho)

    if len(correspondencias) == 1:
        return ("atalho", correspondencias[0])

    return None


def abrir_aplicativo(nome, seguranca):
    if not isinstance(nome, str) or not nome.strip() or len(nome) > 120:
        return "Nome de aplicativo inválido."

    nome = nome.strip()

    destino = _localizar_aplicativo(nome)

    if not destino:
        return (
            f"Não encontrei '{nome}' no Menu Iniciar nem no PATH. "
            "Peça para listar os aplicativos instalados "
            "e tente o nome do atalho."
        )

    try:
        tipo, valor = destino

        if tipo == "atalho":
            os.startfile(str(valor))
        else:
            subprocess.Popen(valor, shell=False)

        seguranca.registrar(
            f"Aplicativo aberto: {nome}"
        )

        return f"Aplicativo aberto: {nome}."

    except FileNotFoundError:
        return "O atalho existe, mas o aplicativo não foi encontrado."

    except Exception as erro:
        seguranca.registrar_erro(erro)

        return (
            f"Não consegui abrir o aplicativo "
            f"({type(erro).__name__})."
        )


def pesquisar_google(termo):
    if not isinstance(termo, str) or not termo.strip():
        return "Diga o que deseja pesquisar."

    termo = termo.strip()[:300]

    url = (
        "https://www.google.com/search?q="
        + quote_plus(termo)
    )

    try:
        webbrowser.open_new_tab(url)

        return f"Pesquisa aberta no navegador: {termo}"

    except Exception:
        return "Não consegui abrir o navegador."
