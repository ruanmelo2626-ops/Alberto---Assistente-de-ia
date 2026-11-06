from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
MODELO_VOSK = BASE_DIR / "modelo" / "vosk-model-pt-fb-v0.1.1-20220516_2113"
PASTA_TRABALHO = BASE_DIR / "workspace"
PASTA_LOGS = PASTA_TRABALHO / "logs"
PASTA_CAPTURAS = PASTA_TRABALHO / "capturas"
PASTA_MEMORIA = PASTA_TRABALHO / "memoria"
OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
OLLAMA_MODELO = "llama3.2:3b"
IDIOMA = "pt-BR"
TAXA_AMOSTRAGEM = 16000
VOLUME_VOZ = 1.0
VOZ_TTS = "pt-BR-AntonioNeural"
LIMITE_TEXTO_ARQUIVO = 8000
LIMITE_HISTORICO = 12
TIMEOUT_OLLAMA = 120
MAX_ACOES_POR_PEDIDO = 4

for pasta in (PASTA_TRABALHO, PASTA_LOGS, PASTA_CAPTURAS, PASTA_MEMORIA):
    pasta.mkdir(parents=True, exist_ok=True)
