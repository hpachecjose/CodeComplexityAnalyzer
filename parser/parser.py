import os 
import ast
import parser
from typing import Dict, List, Tuple, Optional



# -----------------------------
# Descoberta de arquivos
# -----------------------------
def discover_python_files(path: str, config: dict) -> List[str]:
    """
    - Se path é arquivo .py -> retornar [path]
    - Se path é diretório -> caminhar recursivamente
    - Respeitar patterns de exclusão (venv, build, test, regex)
    - Boa prática: suportar .gitignore ou arquivo de exclusão do usuário
    """
    py_files = []
    if os.path.isfile(path) and path.endswith(".py"):
        return [path]
    for root, dirs, files in os.walk(path):
        # exemplo simples de exclusão
        dirs[:] = [d for d in dirs if d not in config.get("exclude_dirs", ["venv", ".git"])]
        for fn in files:
            if fn.endswith(".py"):
                py_files.append(os.path.join(root, fn))
    return py_files




# -----------------------------
# Leitura segura de arquivo
# -----------------------------
def read_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()




def parse_python_file(file_path: str) -> ast.Module:
    """
    - Lê arquivo, parseia com ast.parse(), retorna AST
    - Se SyntaxError, retorna None ou levanta (API do projeto dirá)
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
        return ast.parse(source, filename=file_path)
    except Exception as e:
        print(f"Erro ao parsear {file_path}: {e}")
        return None






# -----------------------------
