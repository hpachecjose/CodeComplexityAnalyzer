"""
Módulo: motor_regras/qualidade/metricas_basicas.py
"""
import ast


class ProfundidadeVisitor(ast.NodeVisitor):
    NOS_QUE_AUMENTAM_PROFUNDIDADE = (
        ast.If, ast.For, ast.While, ast.Try, ast.With, ast.AsyncFor, ast.AsyncWith
    )

    def __init__(self):
        self._profundidade_atual = 0
        self._profundidade_maxima = 0

    def genericamente_visitar_bloco(self, node):
        if isinstance(node, self.NOS_QUE_AUMENTAM_PROFUNDIDADE):
            self._profundidade_atual += 1
            self._profundidade_maxima = max(self._profundidade_maxima, self._profundidade_atual)
            self.generic_visit(node)
            self._profundidade_atual -= 1
        else:
            self.generic_visit(node)

    def visit(self, node):
        self.genericamente_visitar_bloco(node)


def calcular_profundidade_maxima(func_node: ast.AST) -> int:
    v = ProfundidadeVisitor()
    v.visit(func_node)
    return v._profundidade_maxima


def contar_parametros(func_node: ast.FunctionDef) -> int:
    args = func_node.args
    return len(args.args) + len(args.kwonlyargs) + (1 if args.vararg else 0) + (1 if args.kwarg else 0)