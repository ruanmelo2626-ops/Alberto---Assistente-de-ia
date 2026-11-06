import asyncio
import os
import tempfile
import threading
import time

import edge_tts
import pygame

from configuracoes import VOLUME_VOZ, VOZ_TTS


class Voz:

    def __init__(self):

        self.voz = VOZ_TTS

        self.volume = max(
            0.0,
            min(1.0, float(VOLUME_VOZ))
        )

        self.audio_pronto = False
        self._encerrado = False

        self._fala_lock = threading.Lock()
        self._controle_lock = threading.Lock()

        self._parar_evento = threading.Event()

        self._arquivo_atual = None

        try:

            if not pygame.mixer.get_init():

                pygame.mixer.init(
                    frequency=44100,
                    size=-16,
                    channels=2,
                    buffer=512
                )

            pygame.mixer.music.set_volume(self.volume)

            self.audio_pronto = True

            print("[VOZ] Sistema de áudio inicializado.")

        except Exception as erro:

            print(f"[VOZ] Falha ao inicializar áudio: {erro}")

    # --------------------------------------------------------
    # GERAR ÁUDIO
    # --------------------------------------------------------

    async def _gerar_audio(self, texto, caminho):

        comunicacao = edge_tts.Communicate(
            text=texto,
            voice=self.voz
        )

        await comunicacao.save(caminho)

    # --------------------------------------------------------
    # FALAR
    # --------------------------------------------------------

    def falar(self, texto):

        if not isinstance(texto, str) or not texto.strip():
            return False

        if self._encerrado or not self.audio_pronto:
            return False

        texto = texto.strip()[:1500]

        # Impede duas falas simultâneas.
        with self._fala_lock:

            if self._encerrado:
                return False

            self._parar_evento.clear()

            print(f"\nALBERTO: {texto}")

            descritor = None
            caminho = None

            try:

                # Criar arquivo temporário.
                descritor, caminho = tempfile.mkstemp(
                    suffix=".mp3"
                )

                os.close(descritor)
                descritor = None

                self._arquivo_atual = caminho

                # Gerar voz usando Edge TTS.
                asyncio.run(
                    self._gerar_audio(
                        texto,
                        caminho
                    )
                )

                # Verificar se houve cancelamento.
                if self._parar_evento.is_set():
                    return False

                if self._encerrado:
                    return False

                # Carregar e reproduzir.
                with self._controle_lock:

                    if self._parar_evento.is_set():
                        return False

                    pygame.mixer.music.load(caminho)

                    pygame.mixer.music.set_volume(
                        self.volume
                    )

                    pygame.mixer.music.play()

                # Esperar a reprodução terminar.
                while pygame.mixer.music.get_busy():

                    if self._parar_evento.is_set():
                        break

                    if self._encerrado:
                        break

                    time.sleep(0.03)

                return not self._parar_evento.is_set()

            except Exception as erro:

                print(
                    f"[VOZ] Falha na reprodução: "
                    f"{type(erro).__name__}: {erro}"
                )

                return False

            finally:

                # Parar e liberar o áudio.
                try:

                    with self._controle_lock:

                        pygame.mixer.music.stop()

                        try:
                            pygame.mixer.music.unload()
                        except Exception:
                            pass

                except Exception:
                    pass

                # Excluir arquivo temporário.
                if descritor is not None:

                    try:
                        os.close(descritor)
                    except OSError:
                        pass

                if caminho:

                    try:
                        os.remove(caminho)
                    except OSError:
                        pass

                self._arquivo_atual = None

    # --------------------------------------------------------
    # INTERROMPER FALA
    # --------------------------------------------------------

    def parar(self):

        self._parar_evento.set()

        try:

            with self._controle_lock:
                pygame.mixer.music.stop()

        except Exception:
            pass

        return "Reprodução de voz interrompida."

    # --------------------------------------------------------
    # ALTERAR VOLUME
    # --------------------------------------------------------

    def alterar_volume(self, volume):

        try:

            self.volume = max(
                0.0,
                min(1.0, float(volume))
            )

            if self.audio_pronto:

                with self._controle_lock:

                    pygame.mixer.music.set_volume(
                        self.volume
                    )

            return (
                f"Volume ajustado para "
                f"{self.volume:.0%}."
            )

        except (ValueError, TypeError):

            return "Valor de volume inválido."

    # --------------------------------------------------------
    # CONSULTAR ESTADO
    # --------------------------------------------------------

    def esta_falando(self):

        if not self.audio_pronto:
            return False

        try:
            return pygame.mixer.music.get_busy()

        except Exception:
            return False

    # --------------------------------------------------------
    # ENCERRAR
    # --------------------------------------------------------

    def encerrar(self):

        if self._encerrado:
            return

        self._encerrado = True

        self._parar_evento.set()

        try:

            with self._controle_lock:

                pygame.mixer.music.stop()

                try:
                    pygame.mixer.music.unload()
                except Exception:
                    pass

        except Exception:
            pass

        try:

            if self.audio_pronto:
                pygame.mixer.quit()

        except Exception as erro:

            print(
                f"[VOZ] Erro ao encerrar áudio: {erro}"
            )

        self.audio_pronto = False

        print("[VOZ] Sistema de voz encerrado.")
