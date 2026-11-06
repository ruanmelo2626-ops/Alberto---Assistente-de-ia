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

def garantir_ollama():
    """Usa o servidor local existente ou tenta iniciá-lo sem abrir terminal."""
    url = "http://127.0.0.1:11434/api/tags"
    try:
        urllib.request.urlopen(url, timeout=2).close()
        return
    except Exception:
        pass
    try:
        processo = subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL,
                                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        for _ in range(20):
            time.sleep(0.5)
            try:
                urllib.request.urlopen(url, timeout=2).close()
                return
            except Exception:
                continue
    except Exception:
        pass

def main():
    garantir_ollama()
    voz = Voz()
    reconhecimento = None
    seguranca = Seguranca()
    try:
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
        agente = Agente(ia, seguranca, sistema, memoria, mouse, teclado, janelas, processos, navegador)

        voz.falar("Alberto iniciado. Diga olá, Alberto para me chamar.")
        while True:
            print("\nAguardando palavra de ativação...")
            frase = reconhecimento.ouvir_frase()
            print(f"Você: {frase}")
            if not re.search(r"\balberto\b", frase.casefold()):
                continue

            voz.falar("Pode falar.")
            instrucao = reconhecimento.ouvir_frase()
            print(f"Comando: {instrucao}")
            resultado = processar_comando(
                instrucao, voz, ia, seguranca, sistema, memoria,
                mouse, teclado, janelas, processos, None, navegador, agente
            )
            if resultado == "__ENCERRAR__":
                break
            if resultado == "__CANCELAR__":
                voz.falar("Certo. Vou cancelar as próximas ações desta solicitação.")
                continue
            voz.falar(resultado)

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
