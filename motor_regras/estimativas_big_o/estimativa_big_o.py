"""
Módulo: motor_regras/estimativas_big_o/estimativa_big_o.py
Objetivo: transformar fatos estruturais (loops, recursão) em uma estimativa
          de complexidade assintótica. Sempre com confiança declarada,
          nunca como verdade absoluta.
"""

CHAMADAS_CONHECIDAS = {
    "sort": "O(n log n)",
    "sorted": "O(n log n)",
}


def estimar(funcao_info: dict) -> dict:
    """
    Recebe um dict no formato produzido por LoopRecursaoVisitor.function_infos[i]
    Retorna: {"estimativa": str, "confianca": str, "motivo": str}
    """
    loop_depth = funcao_info["max_loop_depth"]
    is_recursive = funcao_info["is_recursive"]
    chamadas_recursivas = funcao_info["chamadas_recursivas"]
    chamadas_conhecidas = funcao_info["chamadas_conhecidas"]

    # 1) Prioridade: chamada conhecida sem loop/recursão adicional
    if chamadas_conhecidas and loop_depth == 0 and not is_recursive:
        estimativa = CHAMADAS_CONHECIDAS.get(chamadas_conhecidas[0], "desconhecido")
        return {
            "estimativa": estimativa,
            "confianca": "alta",
            "motivo": f"chamada a método conhecido ({chamadas_conhecidas[0]})",
        }

    # 2) Recursão presente
    if is_recursive:
        n_chamadas = len(chamadas_recursivas)
        if n_chamadas >= 2:
            return {
                "estimativa": "O(2^n)",
                "confianca": "media",
                "motivo": "duas ou mais chamadas recursivas por invocação (padrão tipo Fibonacci ingênuo)",
            }
        tipo_arg = chamadas_recursivas[0] if chamadas_recursivas else "desconhecido"
        if tipo_arg == "divisao":
            return {
                "estimativa": "O(log n)",
                "confianca": "media",
                "motivo": "recursão com argumento dividido a cada chamada",
            }
        if tipo_arg == "decremento":
            return {
                "estimativa": "O(n)",
                "confianca": "media",
                "motivo": "recursão com argumento decrementado a cada chamada",
            }
        return {
            "estimativa": "desconhecido",
            "confianca": "baixa",
            "motivo": "recursão detectada, mas padrão do argumento não reconhecido",
        }

    # 3) Loops aninhados
    if loop_depth == 0:
        return {"estimativa": "O(1)", "confianca": "media", "motivo": "nenhum loop ou recursão detectado"}
    if loop_depth == 1:
        return {"estimativa": "O(n)", "confianca": "alta", "motivo": "um nível de loop"}
    return {
        "estimativa": f"O(n^{loop_depth})",
        "confianca": "media",
        "motivo": f"{loop_depth} níveis de loop aninhado",
    }