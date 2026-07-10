# language: python
"""
Módulo: analyzer/cyclomatic.py
Objetivo: Percorrer arquivos python, gerar AST, calcular complexidade ciclomática
          por função/método, agregar por arquivo/projeto e exportar resultados.
Entrada: diretório ou lista de arquivos Python
Saída: relatório JSON/CSV com métricas por função, classe, módulo e totais
Regras de negócio (alto-nível):
  1) Ignorar arquivos/trechos conforme .gitignore / padrão de exclusão.
  2) Calcular por escopo (FunctionDef/AsyncFunctionDef, class methods).
  3) Inicializar cada função com 1 e incrementar para cada ponto de decisão.
  4) Normalizar resultados por tamanho (linhas) quando produzir rankings.
  5) Permitir thresholds configuráveis para "alto risco".
  6) Validar com testes de unidade e snippets com complexidade conhecida.
"""

# -----------------------------
# Módulos e utilitários
# -----------------------------
import ast
import os
import json
from typing import Dict, List, Tuple, Optional

class CyclomaticVisitor(ast.NodeVisitor):
    """
    Regras de incremento (padrões recomendados):
      - iniciar cada função com 1
      - If / For / While / With? / AsyncFor  -> +1
      - Each except handler -> +1
      - BoolOp (and/or) with N operands -> + (N - 1)
      - Comprehension: +1 por for/if dentro
      - Conditional expressions (ternary): +1
      - Match (3.10+) -> +1 por case
      - Lambda: opcional +1
      - Early returns: não contam isoladamente (já cobertos por branches)
    Implementação: manter pilha de escopos para suportar funções aninhadas e métodos.
    """
    def __init__(self, config: dict = None):
        self.config = config or {}
        # pilha de contexto para permitir funções aninhadas
        self._scope_stack: List[dict] = []
        # lista final com informações das funções encontradas
        self.function_infos: List[dict] = []

    # helpers de escopo
    def _push_scope(self, name: str, node: ast.AST):
        scope = {
            "name": name,
            "start_line": getattr(node, "lineno", None),
            "complexity": 1,   # regra: cada função começa com 1
            "node": node,
        }
        self._scope_stack.append(scope)

    def _pop_scope(self):
        scope = self._scope_stack.pop()
        # calcular LOC (linhas de código) se possível
        end_line = getattr(scope["node"], "end_lineno", None)
        loc = None
        if end_line and scope["start_line"]:
            loc = end_line - scope["start_line"] + 1
        info = {
            "name": scope["name"],
            "start_line": scope["start_line"],
            "end_line": end_line,
            "loc": loc,
            "complexity": scope["complexity"],
            "node": scope["node"],
        }
        self.function_infos.append(info)

    def _current_scope(self) -> Optional[dict]:
        return self._scope_stack[-1] if self._scope_stack else None

    # visitar definições de função (síncronas e assíncronas)
    def visit_FunctionDef(self, node: ast.FunctionDef):
        self._push_scope(node.name, node)
        # visitar argumentos/defaults -> não contam, mas podem ter lambdas
        self.generic_visit(node)
        self._pop_scope()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self.visit_FunctionDef(node)  # mesmo tratamento

    # classes: abrir escopo apenas para percorrer métodos; não iniciar contagem para classe em si
    def visit_ClassDef(self, node: ast.ClassDef):
        # visitar corpo (métodos) sem iniciar escopo extra para a classe
        self.generic_visit(node)

    # pontos de decisão que incrementam complexidade
    def visit_If(self, node: ast.If):
        scope = self._current_scope()
        if scope:
            scope["complexity"] += 1
        # 'elif' é representado como If em orelse; generic_visit cobre isso
        self.generic_visit(node)

    def visit_For(self, node: ast.For):
        scope = self._current_scope()
        if scope:
            scope["complexity"] += 1
        self.generic_visit(node)

    def visit_AsyncFor(self, node: ast.AsyncFor):
        self.visit_For(node)

    def visit_While(self, node: ast.While):
        scope = self._current_scope()
        if scope:
            scope["complexity"] += 1
        self.generic_visit(node)

    def visit_Try(self, node: ast.Try):
        scope = self._current_scope()
        if scope:
            # cada handler (except) adiciona 1
            scope["complexity"] += len(node.handlers)
        self.generic_visit(node)

    def visit_BoolOp(self, node: ast.BoolOp):
        scope = self._current_scope()
        if scope:
            # N operands -> (N - 1) decisões extras
            n = len(node.values)
            if n > 1:
                scope["complexity"] += (n - 1)
        self.generic_visit(node)

    def visit_IfExp(self, node: ast.IfExp):
        # expressão ternária: cond ? a : b (em python a if cond else b)
        scope = self._current_scope()
        if scope:
            scope["complexity"] += 1
        self.generic_visit(node)

    def visit_Lambda(self, node: ast.Lambda):
        # opcional: contar lambdas como 1
        scope = self._current_scope()
        if scope:
            scope["complexity"] += 1
        self.generic_visit(node)

    def visit_ListComp(self, node: ast.ListComp):
        self._handle_comprehension(node)
    def visit_SetComp(self, node: ast.SetComp):
        self._handle_comprehension(node)
    def visit_DictComp(self, node: ast.DictComp):
        self._handle_comprehension(node)
    def visit_GeneratorExp(self, node: ast.GeneratorExp):
        self._handle_comprehension(node)

    def _handle_comprehension(self, node):
        scope = self._current_scope()
        if scope:
            # cada comprehension tem pelo menos um for; contar +1
            scope["complexity"] += 1
            # se comprehension tem ifs ou mais fors, esses nós serão visitados e contados separadamente
        self.generic_visit(node)

    # Possível extensão: match/case (Python 3.10+)
    def visit_Match(self, node: ast.Match):
        scope = self._current_scope()
        if scope:
            # contar cada case como +1 (ajuste conforme definição)
            scope["complexity"] += len(node.cases)
        self.generic_visit(node)

    # fallback
    def generic_visit(self, node):
        # aqui poderíamos inserir logging, métricas por nó, ou limites de profundidade
        super().generic_visit(node)

    # resumo por arquivo (opcional)
    def file_summary(self):
        complexities = [f["complexity"] for f in self.function_infos]
        if not complexities:
            return {"total_functions": 0, "max_complexity": 0, "average": 0.0}
        return {
            "total_functions": len(complexities),
            "max_complexity": max(complexities),
            "average": sum(complexities) / len(complexities),
        }
