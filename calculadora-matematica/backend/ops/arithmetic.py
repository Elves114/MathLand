"""Operações de aritmética básica."""

import math

from ops.helpers import OpError, fmt, safe_eval, to_int
from ops.registry import op


@op(
    "arit.soma",
    "aritmetica",
    "Soma",
    "Soma dois números inteiros ou decimais (aceita vírgula decimal).",
    [
        {"name": "a", "label": "1.º número", "type": "number", "placeholder": "ex: 12,5"},
        {"name": "b", "label": "2.º número", "type": "number", "placeholder": "ex: 7"},
    ],
    order=1,
)
def soma(a, b):
    return {"display": f"{fmt(a)} + {fmt(b)} = {fmt(a + b)}"}


@op(
    "arit.subtracao",
    "aritmetica",
    "Subtração",
    "Subtrai o segundo número ao primeiro.",
    [
        {"name": "a", "label": "Minuendo", "type": "number", "placeholder": "ex: 20"},
        {"name": "b", "label": "Subtraendo", "type": "number", "placeholder": "ex: 8"},
    ],
    order=2,
)
def subtracao(a, b):
    return {"display": f"{fmt(a)} − {fmt(b)} = {fmt(a - b)}"}


@op(
    "arit.multiplicacao",
    "aritmetica",
    "Multiplicação",
    "Multiplica dois números.",
    [
        {"name": "a", "label": "1.º fator", "type": "number", "placeholder": "ex: 6"},
        {"name": "b", "label": "2.º fator", "type": "number", "placeholder": "ex: 4"},
    ],
    order=3,
)
def multiplicacao(a, b):
    return {"display": f"{fmt(a)} × {fmt(b)} = {fmt(a * b)}"}


@op(
    "arit.divisao",
    "aritmetica",
    "Divisão",
    "Divide o primeiro número pelo segundo.",
    [
        {"name": "a", "label": "Dividendo", "type": "number", "placeholder": "ex: 10"},
        {"name": "b", "label": "Divisor", "type": "number", "placeholder": "ex: 4"},
    ],
    order=4,
)
def divisao(a, b):
    if b == 0:
        raise OpError("Não é possível dividir por zero.")
    quociente = a / b
    steps = [f"{fmt(a)} ÷ {fmt(b)} = {fmt(quociente)}"]
    if abs(a - round(a)) < 1e-9 and abs(b - round(b)) < 1e-9:
        inteiro_a, inteiro_b = int(round(a)), int(round(b))
        resto = inteiro_a - (inteiro_a // inteiro_b) * inteiro_b
        if resto:
            steps.append(
                f"Divisão inteira: {inteiro_a} = {inteiro_b} × {inteiro_a // inteiro_b} + {resto}"
            )
        else:
            steps.append(f"Divisão exata: {inteiro_a} = {inteiro_b} × {inteiro_a // inteiro_b}")
    return {"display": f"{fmt(a)} ÷ {fmt(b)} = {fmt(quociente)}", "steps": steps}


@op(
    "arit.potencia",
    "aritmetica",
    "Potência",
    "Calcula a base elevada ao expoente (ex.: 2^10).",
    [
        {"name": "base", "label": "Base", "type": "number", "placeholder": "ex: 2"},
        {"name": "exp", "label": "Expoente", "type": "number", "placeholder": "ex: 10"},
    ],
    order=5,
)
def potencia(base, exp):
    if base == 0 and exp < 0:
        raise OpError("Zero elevado a um expoente negativo não está definido.")
    if abs(exp) > 10000:
        raise OpError("Expoente demasiado grande.")
    try:
        resultado = base**exp
    except OverflowError:
        raise OpError("Resultado demasiado grande para ser representado.")
    return {
        "display": f"{fmt(base)}^{fmt(exp)} = {fmt(resultado)}",
        "steps": [f"{fmt(base)} elevado a {fmt(exp)} = {fmt(resultado)}"],
    }


@op(
    "arit.raiz",
    "aritmetica",
    "Raiz quadrada",
    "Calcula a raiz quadrada de um número (aceita frações).",
    [
        {"name": "n", "label": "Número", "type": "number", "placeholder": "ex: 144"},
    ],
    order=6,
)
def raiz(n):
    if n < 0:
        raise OpError("Não existe raiz quadrada real de um número negativo.")
    raiz_val = math.sqrt(n)
    exata = abs(raiz_val - round(raiz_val)) < 1e-9
    steps = [f"√{fmt(n)} = {fmt(raiz_val)}"]
    if exata:
        steps.append(f"Raiz exata: {fmt(int(round(raiz_val)))} × {fmt(int(round(raiz_val)))} = {fmt(n)}")
    else:
        steps.append("Valor aproximado (o número não é um quadrado perfeito).")
    return {"display": f"√{fmt(n)} = {fmt(raiz_val)}", "steps": steps}


@op(
    "arit.expressao",
    "aritmetica",
    "Avaliar expressão",
    "Calcula qualquer expressão: parênteses, frações, potências (^), funções (sqrt, log, sin...).",
    [
        {
            "name": "expression",
            "label": "Expressão",
            "type": "expression",
            "placeholder": "ex: (3 + 5) * 2^3 / sqrt(16)",
            "hint": "Multiplicação implícita permitida: 2(3+4) ou 2pi.",
        },
    ],
    order=7,
)
def avaliar_expressao(expression):
    resultado = safe_eval(expression)
    return {
        "display": f"{expression.strip()} = {fmt(resultado)}",
        "steps": [
            "Funções disponíveis: sqrt, abs, round, min, max, pow, log, log10, log2, exp, sin, cos, tan, floor, ceil, factorial.",
            "Constantes disponíveis: pi, e, tau.",
        ],
    }
