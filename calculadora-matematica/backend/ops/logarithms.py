"""Operações com logaritmos."""

import math

from ops.helpers import OpError, fmt
from ops.registry import op


def _validar_base(base):
    if base <= 0:
        raise OpError("A base tem de ser um número positivo.")
    if base == 1:
        raise OpError("A base não pode ser 1 (logaritmo indeterminado).")


def _arredonda(valor):
    """Remove o ruído de ponto flutuante (ex.: log(1000, 10) = 2.9999999999999996)."""
    if abs(valor) < 1e-12:
        return 0.0
    inteiro = round(valor)
    if abs(valor - inteiro) < 1e-12:
        return float(inteiro)
    return valor


@op(
    "log.base",
    "logaritmos",
    "Logaritmo (base livre)",
    "Calcula log_b(x) — a que potência se eleva b para obter x.",
    [
        {"name": "base", "label": "Base (b)", "type": "number", "placeholder": "ex: 2"},
        {"name": "value", "label": "Valor (x)", "type": "number", "placeholder": "ex: 32"},
    ],
    order=1,
)
def logaritmo(base, value):
    _validar_base(base)
    if value <= 0:
        raise OpError("O argumento do logaritmo tem de ser positivo (x > 0).")

    try:
        resultado = _arredonda(math.log(value, base))
    except (ValueError, OverflowError, ZeroDivisionError):
        raise OpError("Não foi possível calcular o logaritmo.")

    steps = [
        f"Por definição: {fmt(base)} ^ y = {fmt(value)}  →  y = log_{fmt(base)}({fmt(value)})",
        f"Mudança de base: ln({fmt(value)}) ÷ ln({fmt(base)}) = "
        f"{fmt(math.log(value))} ÷ {fmt(math.log(base))} = {fmt(resultado)}",
    ]
    if abs(resultado - round(resultado)) < 1e-12:
        steps.append(f"Verificação: {fmt(base)}^{int(round(resultado))} = {fmt(value)} ✓")

    return {
        "display": f"log base {fmt(base)} de {fmt(value)} = {fmt(resultado)}",
        "steps": steps,
        "details": [
            {"label": "Base", "value": fmt(base)},
            {"label": "Logaritmo", "value": fmt(resultado)},
        ],
    }


@op(
    "log.inverso",
    "logaritmos",
    "Equação logarítmica",
    "Resolve log_b(x) = y  →  x = b^y.",
    [
        {"name": "base", "label": "Base (b)", "type": "number", "placeholder": "ex: 10"},
        {"name": "logaritmo", "label": "Logaritmo (y)", "type": "number", "placeholder": "ex: 2.5"},
    ],
    order=2,
)
def equacao_logaritmica(base, logaritmo):
    _validar_base(base)
    try:
        resultado = base**logaritmo
    except OverflowError:
        raise OpError("Resultado demasiado grande.")

    steps = [
        f"Reescrever como potência: x = {fmt(base)} ^ {fmt(logaritmo)} = {fmt(resultado)}",
        f"Verificação: log_{fmt(base)}({fmt(resultado)}) = {fmt(logaritmo)} ✓",
    ]
    return {
        "display": f"x = {fmt(resultado)}",
        "steps": steps,
        "details": [{"label": "x", "value": fmt(resultado)}],
    }
