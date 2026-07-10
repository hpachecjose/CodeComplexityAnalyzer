"""
Módulo: motor_regras/deteccao_loops/deteccao_loops.py
Objetivo: coletar fatos estruturais por função — não decide Big-O aqui,
          apenas descreve o que existe (loops, profundidade, recursão).
"""
import ast
from typing import List, Optional


class LoopRecursaoVisitor(ast.NodeVisitor):
    def __init__(self):
        self._scope_stack: List[dict] = []
        self.function_infos: List[dict] = []
        self._current_depth = 0

    def _push_scope(self, name: str):
        self._scope_stack.append({
            "name": name,
            "max_loop_depth": 0,
            "loop_count": 0,
            "is_recursive": False,
            "chamadas_recursivas": [],   # guarda os args de cada chamada recursiva
            "chamadas_conhecidas": [],   # ex.: sort(), sorted()
        })
        self._current_depth = 0

    def _pop_scope(self):
        return self._scope_stack.pop()

    def _current_scope(self) -> Optional[dict]:
        return self._scope_stack[-1] if self._scope_stack else None

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self._push_scope(node.name)
        self.generic_visit(node)
        info = self._pop_scope()
        self.function_infos.append(info)

    visit_AsyncFunctionDef = visit_FunctionDef

    def _visit_loop(self, node):
        scope = self._current_scope()
        if scope:
            self._current_depth += 1
            scope["loop_count"] += 1
            scope["max_loop_depth"] = max(scope["max_loop_depth"], self._current_depth)
        self.generic_visit(node)
        if scope:
            self._current_depth -= 1

    def visit_For(self, node: ast.For):
        self._visit_loop(node)

    visit_AsyncFor = visit_For

    def visit_While(self, node: ast.While):
        self._visit_loop(node)

    def visit_Call(self, node: ast.Call):
        scope = self._current_scope()
        if scope:
            # recursão: chamada ao próprio nome da função no escopo atual
            if isinstance(node.func, ast.Name) and node.func.id == scope["name"]:
                scope["is_recursive"] = True
                scope["chamadas_recursivas"].append(self._descrever_argumento(node))
            # chamadas conhecidas cuja complexidade já é documentada
            elif isinstance(node.func, ast.Attribute) and node.func.attr in ("sort",):
                scope["chamadas_conhecidas"].append("sort")
            elif isinstance(node.func, ast.Name) and node.func.id == "sorted":
                scope["chamadas_conhecidas"].append("sorted")
        self.generic_visit(node)

    def _descrever_argumento(self, call_node: ast.Call) -> str:
        """
        Heurística simples: olha o primeiro argumento da chamada recursiva
        e tenta classificar como 'divisao' (n // 2), 'decremento' (n - 1)
        ou 'desconhecido'.
        """
        if not call_node.args:
            return "sem_argumentos"
        arg = call_node.args[0]
        if isinstance(arg, ast.BinOp):
            if isinstance(arg.op, (ast.FloorDiv, ast.Div)):
                return "divisao"
            if isinstance(arg.op, ast.Sub):
                return "decremento"
        return "desconhecido"