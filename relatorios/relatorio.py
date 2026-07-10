
import ast
import os
import json
from typing import Dict, List, Tuple, Optional


# -----------------------------
# Thresholds e sinalizações
# -----------------------------
import csv

def apply_thresholds(results: dict, config: dict):
    """
    - Percorrer resultados e marcar funções com complexity > warn/critical.
    - Regras de negócio: thresholds configuráveis; regra padrão:
        warn: 10, error: 20
    - Registrar também "hotspots" top-N para dashboard.
    """
    warn = config.get("warn_threshold", 10)
    error = config.get("error_threshold", 20)
    hotspots = []
    for fpath, info in results["by_file"].items():
        funcs = info.get("functions", [])
        for fi in funcs:
            if fi["complexity"] >= error:
                fi["flag"] = "error"
            elif fi["complexity"] >= warn:
                fi["flag"] = "warn"
            else:
                fi["flag"] = "ok"
            hotspots.append((fi["complexity"], fpath, fi["name"]))
    # ordenar e guardar top 10
    hotspots.sort(reverse=True)
    results["summary"]["hotspots"] = hotspots[:10]

def exportar_csv(results: dict, output_filepath: str):
    """
    Exporta o dicionário de resultados para um arquivo CSV estruturado.
    """
    # Garantir que o diretório base do CSV existe
    os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
    
    with open(output_filepath, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = [
            "Arquivo", "Funcao", "Linha_Inicio", "Linha_Fim", "LOC", 
            "Complexidade_Ciclomatica", "Max_Loop_Depth", "Qtd_Loops", 
            "Recursiva", "Estimativa_BigO", "Confianca_BigO", 
            "Profundidade_AST", "Qtd_Parametros", "Status"
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for fpath, info in results.get("by_file", {}).items():
            for func in info.get("functions", []):
                writer.writerow({
                    "Arquivo": fpath,
                    "Funcao": func.get("name"),
                    "Linha_Inicio": func.get("start_line"),
                    "Linha_Fim": func.get("end_line"),
                    "LOC": func.get("loc"),
                    "Complexidade_Ciclomatica": func.get("complexity"),
                    "Max_Loop_Depth": func.get("max_loop_depth"),
                    "Qtd_Loops": func.get("loop_count"),
                    "Recursiva": "Sim" if func.get("is_recursive") else "Nao",
                    "Estimativa_BigO": func.get("big_o_estimativa"),
                    "Confianca_BigO": func.get("big_o_confianca"),
                    "Profundidade_AST": func.get("max_ast_depth"),
                    "Qtd_Parametros": func.get("parameters_count"),
                    "Status": func.get("flag")
                })
