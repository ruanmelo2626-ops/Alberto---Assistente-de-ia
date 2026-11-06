from configuracoes import MODELO_VOSK, OLLAMA_MODELO

import re
import subprocess
import urllib.request
import time

from reconhecimento import Reconhecedor
from voz import Voz
from inteligencia import Inteligencia
from seguranca import Seguranca
from sistema import Sistema
from memoria import Memoria
from controle_mouse import ControleMouse
from controle_teclado import ControleTeclado
from controle_janelas import ControleJanelas
from processos import Processos
from navegador import Navegador
from comandos import processar_comando
from agente import Agente


def normalizar(texto):
    return str(texto).casefold().strip()


def detectar_ativacao(frase):
    return bool(re.search(r"\balberto\b", normalizar(frase)))


def garantir_ollama():
    """Verifica o Ollama e tenta iniciar o servidor se necessário."""
    url = "http://127.0.0.1:11434/api/tags"

    try:
        urllib.request.urlopen(url, timeout=2).close()
        print("Ollama já está funcionando.")
        return True
    except Exception:
        pass

    try:
        subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
        )

        for _ in range(20):
            time.sleep(0.5)

            try:
                urllib.request.urlopen(url, timeout=2).close()
                print("Servidor Ollama iniciado.")
                return True
            except Exception:
                continue

    except Exception as erro:
        print(f"Não foi possível iniciar o Ollama: {erro}")

    print("AVISO: não foi possível confirmar o funcionamento do Ollama.")
    return False


def aguardar_ativacao(reconhecimento, voz):
    """Espera a palavra Alberto para iniciar uma sessão contínua."""

    while True:
        print("\nAguardando ativação: diga Olá, Alberto.")

        frase = reconhecimento.ouvir_frase()

        if not frase:
            continue

        print(f"Você: {frase}")

        if detectar_ativacao(frase):
            voz.falar("Pode falar. Estou ouvindo.")
            return True


def executar_comando(
    instrucao, voz, ia, seguranca, sistema, memoria,
    mouse, teclado, janelas, processos, navegador, agente
):
    """Envia a solicitação para o sistema de comandos."""

    try:
        resultado = processar_comando(
            instrucao,
            voz,
            ia,
            seguranca,
            sistema,
            memoria,
            mouse,
            teclado,
            janelas,
            processos,
            None,
            navegador,
            agente
        )

        return resultado

    except Exception as erro:
        seguranca.registrar_erro(erro)
        print(f"Erro ao executar solicitação: {erro}")
        return "Ocorreu um erro ao executar essa solicitação."


def main():
    voz = Voz()
    reconhecimento = None
    seguranca = Seguranca()

    try:
        garantir_ollama()

        reconhecimento = Reconhecedor(MODELO_VOSK)
        ia = Inteligencia()

        print(f"Modelo de IA: {OLLAMA_MODELO}")
        print(f"Modelo de voz: {MODELO_VOSK}")

        sistema = Sistema()
        memoria = Memoria()

        mouse = ControleMouse(seguranca)
        teclado = ControleTeclado(seguranca)
        janelas = ControleJanelas(seguranca)
        processos = Processos()
        navegador = Navegador()

        agente = Agente(
            ia,
            seguranca,
            sistema,
            memoria,
            mouse,
            teclado,
            janelas,
            processos,
            navegador
        )

        voz.falar("Alberto iniciado.")

        # Primeira etapa: ativação por voz.
        aguardar_ativacao(reconhecimento, voz)

        # Segunda etapa: sessão contínua.
        while True:
            print("\nALBERTO está ouvindo...")

            instrucao = reconhecimento.ouvir_frase()

            if not instrucao:
                continue

            print(f"Você: {instrucao}")

            resultado = executar_comando(
                instrucao,
                voz,
                ia,
                seguranca,
                sistema,
                memoria,
                mouse,
                teclado,
                janelas,
                processos,
                navegador,
                agente
            )

            if resultado == "__ENCERRAR__":
                break

            if resultado == "__CANCELAR__":
                voz.falar("Solicitação cancelada.")
                continue

            if resultado:
                voz.falar(str(resultado))

    except KeyboardInterrupt:
        print("\nEncerramento solicitado pelo teclado.")

    except Exception as erro:
        seguranca.registrar_erro(erro)
        print(f"Erro ao iniciar ALBERTO: {erro}")

    finally:
        if reconhecimento:
            reconhecimento.fechar()

        voz.falar("ALBERTO encerrado.")
        voz.encerrar()


if __name__ == "__main__":
    main()
