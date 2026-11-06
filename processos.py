import psutil

class Processos:
    """Consulta processos; não encerra nem altera processos."""

    def listar(self, limite=20):
        linhas = []
        for p in psutil.process_iter(["pid", "name", "status", "memory_info"]):
            try:
                info = p.info
                memoria = info["memory_info"].rss / (1024 * 1024) if info["memory_info"] else 0
                linhas.append(f'{info["pid"]} | {info["name"]} | {info["status"]} | {memoria:.1f} MB')
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return "\n".join(linhas[:max(1, min(limite, 50))])

    def pesquisar(self, termo):
        termo = str(termo).casefold()
        encontrados = []
        for p in psutil.process_iter(["pid", "name"]):
            try:
                if termo in (p.info["name"] or "").casefold():
                    encontrados.append(f'{p.info["pid"]} | {p.info["name"]}')
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return "\n".join(encontrados[:30]) if encontrados else "Nenhum processo encontrado."

    def resumo(self):
        return f"Processos em execução: {len(psutil.pids())}"
