import json
import queue
import time
import sounddevice as sd
from vosk import Model, KaldiRecognizer
from configuracoes import TAXA_AMOSTRAGEM

class Reconhecedor:
    def __init__(self, caminho_modelo):
        if not caminho_modelo.exists() or not any(caminho_modelo.iterdir()):
            raise FileNotFoundError(f"Modelo Vosk não encontrado: {caminho_modelo}")
        self.modelo = Model(str(caminho_modelo))
        self.rec = KaldiRecognizer(self.modelo, TAXA_AMOSTRAGEM)
        self.fila = queue.Queue()
        self.stream = None
        self.ativo = False
        self.tempo_maximo = 15

    def _callback(self, indata, frames, tempo, status):
        if status:
            print(f"Áudio: {status}")
        self.fila.put(bytes(indata))

    def ouvir_frase(self):
        self.fila = queue.Queue()
        self.rec.Reset()
        self.ativo = True
        try:
            with sd.RawInputStream(
                samplerate=TAXA_AMOSTRAGEM,
                blocksize=8000,
                dtype="int16",
                channels=1,
                callback=self._callback,
            ) as stream:
                self.stream = stream
                inicio = time.monotonic()
                ultimo_audio = inicio
                while self.ativo:
                    try:
                        dados = self.fila.get(timeout=0.5)
                    except queue.Empty:
                        if time.monotonic() - inicio >= self.tempo_maximo:
                            return ""
                        continue
                    ultimo_audio = time.monotonic()
                    if self.rec.AcceptWaveform(dados):
                        resultado = json.loads(self.rec.Result())
                        texto = resultado.get("text", "").strip()
                        if texto:
                            return texto
                    if time.monotonic() - ultimo_audio > 8:
                        parcial = json.loads(self.rec.FinalResult()).get("text", "").strip()
                        if parcial:
                            return parcial
        finally:
            self.stream = None
            self.ativo = False
        return ""

    def fechar(self):
        self.ativo = False
        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception:
                pass
