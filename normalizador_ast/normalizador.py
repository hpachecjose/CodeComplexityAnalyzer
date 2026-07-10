def normalizar(tree):
    """
    Hoje: identidade, pois o motor de regras já entende ast nativa.
    Quando você migrar para Tree-sitter (Fase 3 do roadmap), esta função
    passa a converter a árvore de qualquer linguagem para um formato
    interno comum, para o motor de regras não precisar saber se veio
    de Python, JS ou C.
    """
    return tree