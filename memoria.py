import json
from pathlib import Path
from configuracoes import PASTA_MEMORIA

class Memoria:
    """Armazena notas explícitas em JSON; não grava dados pessoais automaticamente."""

    def __init__(self):
        self.arquivo = PASTA_MEMORIA / "notas.json"
        PASTA_MEMORIA.mkdir(parents=True, exist_ok=True)
        if not self.arquivo.exists():
            self._salvar([])

    def _carregar(self):
        try:
            return json.loads(self.arquivo.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []

    def _salvar(self, dados):
        self.arquivo.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")

    def adicionar(self, nota):
        nota = str(nota).strip()
        if not nota or len(nota) > 500:
            return "A nota deve ter entre 1 e 500 caracteres."
        dados = self._carregar()
        dados.append(nota)
        self._salvar(dados[-200:])
        return "Nota salva na memória local."

    def listar(self):
        dados = self._carregar()
        return "\n".join(f"{i+1}. {n}" for i, n in enumerate(dados)) if dados else "A memória está vazia."

    def limpar(self, seguranca):
        if not seguranca.confirmar_acao("apagar todas as notas da memória local"):
            return "Limpeza cancelada."
        self._salvar([])
        return "Notas apagadas."
