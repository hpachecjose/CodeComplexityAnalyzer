
import ast
import os
import json

from parser.parser import discover_python_files, read_file
from motor_regras.complexidade_ciclomatica.analise_ciclomatica import CyclomaticVisitor
from motor_regras.deteccao_loops.deteccao_loops import LoopRecursaoVisitor
from motor_regras.estimativas_big_o.estimativa_big_o import estimar
from motor_regras.qualidade.metricas_basicas import calcular_profundidade_maxima, contar_parametros
from relatorios.relatorio import apply_thresholds

def analyze_path(path: str, config: dict) -> dict:
    files = discover_python_files(path, config)
    results = {"by_file": {}, "summary": {}}
    
    total_funcs = 0
    for fpath in files:
        try:
            content = read_file(fpath)
            tree = ast.parse(content)
            
            visitor = CyclomaticVisitor(config)
            visitor.visit(tree)
            
            loop_visitor = LoopRecursaoVisitor()
            loop_visitor.visit(tree)
            
            merged_funcs = []
            for c_info, l_info in zip(visitor.function_infos, loop_visitor.function_infos):
                if c_info["name"] == l_info["name"]:
                    node = c_info.pop("node")
                    
                    big_o_info = estimar(l_info)
                    max_depth = calcular_profundidade_maxima(node)
                    params_count = contar_parametros(node)
                    
                    c_info.update({
                        "max_loop_depth": l_info["max_loop_depth"],
                        "loop_count": l_info["loop_count"],
                        "is_recursive": l_info["is_recursive"],
                        "big_o_estimativa": big_o_info["estimativa"],
                        "big_o_confianca": big_o_info["confianca"],
                        "max_ast_depth": max_depth,
                        "parameters_count": params_count
                    })
                    merged_funcs.append(c_info)
            
            visitor.function_infos = merged_funcs

            results["by_file"][fpath] = {
                "functions": visitor.function_infos,
                "summary": visitor.file_summary()
            }
            total_funcs += len(visitor.function_infos)
        except Exception as e:
            results["by_file"][fpath] = {"error": str(e)}
            
    results["summary"]["total_files"] = len(files)
    results["summary"]["total_functions"] = total_funcs
    
    apply_thresholds(results, config)
    return results

# -----------------------------
# CLI / integração (exemplo de uso)
# -----------------------------
def main_cli():
    """
    - Parsear argumentos (path, output, thresholds)
    - Carregar config padrão e sobrescrever com flags
    - Chamar analyze_path e exportar JSON/CSV
    """
    import argparse
    parser = argparse.ArgumentParser(description="Análise de complexidade ciclomática")
    parser.add_argument("path", help="Arquivo ou diretório para analisar")
    parser.add_argument("--output", "-o", help="Arquivo JSON de saída", default="cc_report.json")
    parser.add_argument("--warn", type=int, default=10)
    parser.add_argument("--error", type=int, default=20)
    args = parser.parse_args()

    config = {"warn_threshold": args.warn, "error_threshold": args.error, "exclude_dirs": ["venv", ".git"]}
    res = analyze_path(args.path, config)
    with open(args.output, "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=2, ensure_ascii=False)
    print(f"Relatório gerado em {args.output}")

if __name__ == "__main__":
    main_cli()
