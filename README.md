# ALBERTO — assistente local para Windows

## Iniciar sem VS Code
1. Extraia a pasta inteira em um local permanente.
2. Instale Python 3.12, Ollama e o modelo local `llama3.2:3b` (`ollama pull llama3.2:3b`).
3. Coloque o modelo Vosk em `modelo/vosk-model-pt-fb-v0.1.1-20220516_2113`.
4. Execute `INSTALAR_DEPENDENCIAS.bat` uma vez.
5. Execute `INICIAR_ALBERTO.bat`. Para criar um atalho na área de trabalho, execute `INSTALAR_ATALHO.bat`.

O ALBERTO tenta iniciar o servidor Ollama automaticamente se ele ainda não estiver ativo.

## Exemplos
- “Que horas são?”
- “Abra o YouTube.”
- “Que horas são e abra o YouTube.” (duas ações em sequência)
- “Alberto, cancelar.” (cancela a solicitação antes de iniciar novas ações)
- “Encerre o Alberto.”

## Observações importantes
- O projeto continua em Python; não há ganho automático em migrar para outra linguagem. O instalador cria um atalho do Windows, então não é necessário abrir o VS Code.
- O cancelamento por voz é reconhecido como uma nova instrução. Nesta versão, ele impede novas ações quando recebido entre solicitações; uma ação já iniciada não pode ser interrompida instantaneamente enquanto o agente estiver ocupado. Isso exige um listener concorrente dedicado e será uma etapa separada.
- O reconhecimento depende do microfone, do modelo Vosk e do ruído ambiente. O código agora tem limite de espera para não ficar bloqueado indefinidamente.
- Resultados das ferramentas são apresentados diretamente, sem pedir ao modelo para reescrever o que aconteceu. Diagnósticos ficam em `workspace/logs/diagnostico_agente.jsonl`.
- A IA não recebe shell irrestrito. Ações de teclado, mouse, arquivos e janelas continuam sujeitas às proteções do projeto.
