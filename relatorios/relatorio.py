
import ast
import os
import json
from typing import Dict, List, Tuple, Optional


# -----------------------------
# Thresholds e sinalizações
# -----------------------------
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
