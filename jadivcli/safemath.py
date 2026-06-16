"""A safe arithmetic evaluator.

The classic ``calc`` command used Python's :func:`eval`, which executes
arbitrary code. This module replaces it with an evaluator that walks the
abstract syntax tree and only allows numeric literals, the common arithmetic
operators, parentheses, and a small whitelist of :mod:`math` helpers. Anything
else raises :class:`CalcError`.
"""

from __future__ import annotations

import ast
import math
import operator
from typing import Callable, Dict


class CalcError(ValueError):
    """Raised when an expression is invalid or uses disallowed features."""


# Binary operators we accept.
_BIN_OPS: Dict[type, Callable[[float, float], float]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

# Unary operators we accept.
_UNARY_OPS: Dict[type, Callable[[float], float]] = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}

# Names that resolve to constants or single-argument math functions.
_ALLOWED_NAMES: Dict[str, object] = {
    "pi": math.pi,
    "e": math.e,
    "tau": math.tau,
}
_ALLOWED_FUNCS: Dict[str, Callable[..., float]] = {
    "sqrt": math.sqrt,
    "abs": abs,
    "round": round,
    "floor": math.floor,
    "ceil": math.ceil,
    "log": math.log,
    "log2": math.log2,
    "log10": math.log10,
    "exp": math.exp,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "pow": math.pow,
    "min": min,
    "max": max,
}


def _eval(node: ast.AST) -> float:
    if isinstance(node, ast.Constant):
        if isinstance(node.value, bool) or not isinstance(node.value, (int, float)):
            raise CalcError("only numbers are allowed")
        return node.value
    if isinstance(node, ast.BinOp):
        op = _BIN_OPS.get(type(node.op))
        if op is None:
            raise CalcError(f"operator '{type(node.op).__name__}' is not allowed")
        return op(_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp):
        op = _UNARY_OPS.get(type(node.op))
        if op is None:
            raise CalcError(f"operator '{type(node.op).__name__}' is not allowed")
        return op(_eval(node.operand))
    if isinstance(node, ast.Name):
        if node.id in _ALLOWED_NAMES:
            return _ALLOWED_NAMES[node.id]
        raise CalcError(f"unknown name '{node.id}'")
    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name) or node.func.id not in _ALLOWED_FUNCS:
            raise CalcError("only a fixed set of math functions is allowed")
        if node.keywords:
            raise CalcError("keyword arguments are not allowed")
        args = [_eval(arg) for arg in node.args]
        return _ALLOWED_FUNCS[node.func.id](*args)
    raise CalcError("unsupported expression")


def evaluate(expression: str) -> float:
    """Evaluate an arithmetic ``expression`` and return its numeric result.

    Raises :class:`CalcError` for empty, malformed, or disallowed expressions.
    """
    expression = expression.strip()
    if not expression:
        raise CalcError("empty expression")
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as exc:
        raise CalcError("could not parse the expression") from exc
    return _eval(tree.body)
