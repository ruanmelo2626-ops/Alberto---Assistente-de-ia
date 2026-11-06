import json
import queue
import time
import threading

import sounddevice as sd
from vosk import Model, KaldiRecognizer

from configuracoes import TAXA_AMOSTRAGEM


class Reconhecedor:

    def __init__(self, caminho_modelo):

        if not caminho_modelo.exists() or not any(caminho_modelo.iterdir()):
            raise FileNotFoundError(
                f"Modelo Vosk não encontrado: {caminho_modelo}"
            )

        print("[VOZ] Carregando modelo Vosk...")

        self.modelo = Model(str(caminho_modelo))

        self.rec = KaldiRecognizer(
            self.modelo,
            TAXA_AMOSTRAGEM
        )

        self.fila = queue.Queue(maxsize=100)

        self.stream = None

        self.ativo = False

        self.lock = threading.Lock()

        # Tempo máximo aguardando uma frase.
        self.tempo_maximo = 15

        # Tempo de estabilidade do reconhecimento parcial.
        self.tempo_silencio = 1.2

        # Tempo máximo de uma frase.
        self.tempo_maximo_frase = 15

        self.bloco_audio = 4000

        print("[VOZ] Modelo Vosk carregado.")

    # --------------------------------------------------------
    # CALLBACK DE ÁUDIO
    # --------------------------------------------------------

    def _callback(self, indata, frames, tempo, status):

        if status:
            print(f"[ÁUDIO] {status}")

        if not self.ativo:
            return

        try:
            self.fila.put_nowait(bytes(indata))

        except queue.Full:
            # Evita crescimento ilimitado da fila.
            pass

    # --------------------------------------------------------
    # REINICIAR RECONHECIMENTO
    # --------------------------------------------------------

    def _reiniciar_reconhecimento(self):

        self.rec.Reset()

        while True:
            try:
                self.fila.get_nowait()

            except queue.Empty:
                break

    # --------------------------------------------------------
    # RECONHECER UMA FRASE
    # --------------------------------------------------------

    def ouvir_frase(self):

        with self.lock:

            return self._ouvir_frase_interno()

    def _ouvir_frase_interno(self):

        if not self.ativo:

            self._reiniciar_reconhecimento()

        inicio = time.monotonic()

        ultimo_texto = ""

        ultima_mudanca = inicio

        texto_reconhecido = ""

        self.ativo = True

        try:

            with sd.RawInputStream(
                samplerate=TAXA_AMOSTRAGEM,
                blocksize=self.bloco_audio,
                dtype="int16",
                channels=1,
                callback=self._callback
            ) as stream:

                self.stream = stream

                print("[MICROFONE] Escutando...")

                while self.ativo:

                    agora = time.monotonic()

                    # Limite total de espera.
                    if agora - inicio >= self.tempo_maximo:
                        break

                    # Capturar áudio.
                    try:

                        dados = self.fila.get(
                            timeout=0.25
                        )

                    except queue.Empty:
                        continue

                    # Verificar se Vosk identificou uma frase.
                    if self.rec.AcceptWaveform(dados):

                        resultado = json.loads(
                            self.rec.Result()
                        )

                        texto = resultado.get(
                            "text",
                            ""
                        ).strip()

                        if texto:

                            texto_reconhecido = texto

                            print(
                                f"[RECONHECIMENTO] {texto}"
                            )

                            return texto

                    # Consultar reconhecimento parcial.
                    parcial_json = self.rec.PartialResult()

                    try:

                        parcial = json.loads(
                            parcial_json
                        ).get(
                            "partial",
                            ""
                        ).strip()

                    except json.JSONDecodeError:
                        parcial = ""

                    agora = time.monotonic()

                    if parcial:

                        if parcial != ultimo_texto:

                            ultimo_texto = parcial

                            ultima_mudanca = agora

                        # Se o reconhecimento ficou estável,
                        # considerar que o usuário terminou.
                        elif agora - ultima_mudanca >= self.tempo_silencio:

                            resultado = json.loads(
                                self.rec.FinalResult()
                            )

                            texto = resultado.get(
                                "text",
                                ""
                            ).strip()

                            if texto:

                                print(
                                    f"[RECONHECIMENTO] {texto}"
                                )

                                return texto

                    # Limite de duração de uma frase.
                    if agora - inicio >= self.tempo_maximo_frase:

                        resultado = json.loads(
                            self.rec.FinalResult()
                        )

                        texto = resultado.get(
                            "text",
                            ""
                        ).strip()

                        if texto:
                            return texto

                # Recuperar eventual resultado final.
                resultado = json.loads(
                    self.rec.FinalResult()
                )

                texto = resultado.get(
                    "text",
                    ""
                ).strip()

                if texto:
                    return texto

                return texto_reconhecido

        except sd.PortAudioError as erro:

            print(
                f"[MICROFONE] Erro de áudio: {erro}"
            )

            return ""

        except Exception as erro:

            print(
                f"[RECONHECIMENTO] Erro: {erro}"
            )

            return ""

        finally:

            self.stream = None

            self.ativo = False

    # --------------------------------------------------------
    # ENCERRAMENTO
    # --------------------------------------------------------

    def fechar(self):

        self.ativo = False

        if self.stream:

            try:
                self.stream.stop()
                self.stream.close()

            except Exception:
                pass

            self.stream = None

        print("[VOZ] Reconhecimento encerrado.")
