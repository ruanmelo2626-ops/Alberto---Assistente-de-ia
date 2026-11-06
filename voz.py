import asyncio
import os
import tempfile
import time
import edge_tts
import pygame
from configuracoes import VOLUME_VOZ, VOZ_TTS

class Voz:
    def __init__(self):
        self.voz = VOZ_TTS
        self.volume = max(0.0, min(1.0, float(VOLUME_VOZ)))
        self.audio_pronto = False
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            pygame.mixer.music.set_volume(self.volume)
            self.audio_pronto = True
        except Exception as erro:
            print(f"Áudio indisponível: {erro}")

    async def _gerar_audio(self, texto, caminho):
        comunicacao = edge_tts.Communicate(texto, self.voz)
        await comunicacao.save(caminho)

    def falar(self, texto):
        if not isinstance(texto, str) or not texto.strip():
            return
        print(f"ALBERTO: {texto}")
        if not self.audio_pronto:
            return
        descritor, caminho = tempfile.mkstemp(suffix=".mp3")
        os.close(descritor)
        try:
            asyncio.run(self._gerar_audio(texto[:1500], caminho))
            pygame.mixer.music.load(caminho)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.05)
        except Exception as erro:
            print(f"Falha na voz: {erro}")
        finally:
            try:
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
            except Exception:
                pass
            try:
                os.remove(caminho)
            except OSError:
                pass

    def alterar_volume(self, volume):
        self.volume = max(0.0, min(1.0, float(volume)))
        if self.audio_pronto:
            pygame.mixer.music.set_volume(self.volume)
        return f"Volume ajustado para {self.volume:.0%}."

    def encerrar(self):
        if self.audio_pronto:
            try:
                pygame.mixer.quit()
            except Exception:
                pass
