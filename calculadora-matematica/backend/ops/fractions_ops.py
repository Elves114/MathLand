"""Operações com frações."""

import math
from fractions import Fraction

from ops.helpers import OpError, decimal_places, fmt, is_terminating_decimal, to_number
from ops.registry import op


def _lcm(a, b):
    return abs(a * b) // math.gcd(a, b)


def _show(value: Fraction) -> str:
    return str(value)


@op(
    "frac.soma",
    "fracoes",
    "Somar frações",
    "Soma de duas frações. Aceita também números mistos (ex.: 1 1/2).",
    [
        {"name": "a", "label": "1.ª fração", "type": "fraction", "placeholder": "ex: 1/2"},
        {"name": "b", "label": "2.ª fração", "type": "fraction", "placeholder": "ex: 1/3"},
    ],
    order=1,
)
def frac_soma(a, b):
    resultado = a + b
    mcm = _lcm(a.denominator, b.denominator)
    steps = []
    if mcm != a.denominator or mcm != b.denominator:
        steps.append(
            f"MCM({a.denominator}, {b.denominator}) = {mcm} → "
            f"{_show(Fraction(a.numerator * (mcm // a.denominator), mcm))} + "
            f"{_show(Fraction(b.numerator * (mcm // b.denominator), mcm))} = {_show(resultado)}"
        )
    steps.append(f"Resultado simplificado: {_show(resultado)} ≈ {fmt(float(resultado))}")
    return {"display": f"{_show(a)} + {_show(b)} = {_show(resultado)}", "steps": steps}


@op(
    "frac.subtracao",
    "fracoes",
    "Subtrair frações",
    "Subtrai a segunda fração à primeira.",
    [
        {"name": "a", "label": "1.ª fração", "type": "fraction", "placeholder": "ex: 3/4"},
        {"name": "b", "label": "2.ª fração", "type": "fraction", "placeholder": "ex: 1/6"},
    ],
    order=2,
)
def frac_subtracao(a, b):
    resultado = a - b
    mcm = _lcm(a.denominator, b.denominator)
    steps = []
    if mcm != a.denominator or mcm != b.denominator:
        steps.append(
            f"MCM({a.denominator}, {b.denominator}) = {mcm} → "
            f"{_show(Fraction(a.numerator * (mcm // a.denominator), mcm))} − "
            f"{_show(Fraction(b.numerator * (mcm // b.denominator), mcm))} = {_show(resultado)}"
        )
    steps.append(f"Resultado simplificado: {_show(resultado)} ≈ {fmt(float(resultado))}")
    return {"display": f"{_show(a)} − {_show(b)} = {_show(resultado)}", "steps": steps}


@op(
    "frac.multiplicacao",
    "fracoes",
    "Multiplicar frações",
    "Multiplica numeradores entre si e denominadores entre si.",
    [
        {"name": "a", "label": "1.ª fração", "type": "fraction", "placeholder": "ex: 2/3"},
        {"name": "b", "label": "2.ª fração", "type": "fraction", "placeholder": "ex: 5/7"},
    ],
    order=3,
)
def frac_multiplicacao(a, b):
    resultado = a * b
    steps = [
        f"{a.numerator} × {b.numerator} = {a.numerator * b.numerator} (numeradores)",
        f"{a.denominator} × {b.denominator} = {a.denominator * b.denominator} (denominadores)",
        f"Simplificando: {_show(resultado)} ≈ {fmt(float(resultado))}",
    ]
    return {"display": f"{_show(a)} × {_show(b)} = {_show(resultado)}", "steps": steps}


@op(
    "frac.divisao",
    "fracoes",
    "Dividir frações",
    "Divide a primeira fração pela segunda (multiplica pelo inverso).",
    [
        {"name": "a", "label": "1.ª fração", "type": "fraction", "placeholder": "ex: 3/5"},
        {"name": "b", "label": "2.ª fração", "type": "fraction", "placeholder": "ex: 2/9"},
    ],
    order=4,
)
def frac_divisao(a, b):
    if b == 0:
        raise OpError("Não é possível dividir por uma fração com valor zero.")
    inverso = Fraction(b.denominator, b.numerator)
    resultado = a * inverso
    steps = [
        f"Inverso de {_show(b)} = {_show(inverso)}",
        f"{_show(a)} × {_show(inverso)} = {_show(resultado)}",
        f"Resultado: {_show(resultado)} ≈ {fmt(float(resultado))}",
    ]
    return {"display": f"{_show(a)} ÷ {_show(b)} = {_show(resultado)}", "steps": steps}


def _decimal_places(text: str) -> int:
    text = text.strip().replace(",", ".")
    return len(text.split(".", 1)[1]) if "." in text else 0


@op(
    "frac.simplificar",
    "fracoes",
    "Simplificar fração",
    "Reduz uma fração aos termos mais simples (dividindo numerador e denominador pelo MDC).",
    [
        {"name": "value", "label": "Fração", "type": "text", "placeholder": "ex: 36/48"},
    ],
    order=5,
)
def frac_simplificar(value):
    text = str(value).strip().replace(",", ".")
    if "/" not in text:
        raise OpError("Escreva a fração no formato numerador/denominador (ex.: 36/48).")
    num_text, _, den_text = text.partition("/")
    if not num_text.strip() or not den_text.strip():
        raise OpError("Formato inválido. Exemplo correto: 36/48.")

    try:
        numerador_f = to_number(num_text, "numerador")
        denominador_f = to_number(den_text, "denominador")
    except OpError as exc:
        raise OpError(f"Fração inválida ({exc}).")

    if denominador_f == 0:
        raise OpError("O denominador não pode ser zero.")

    # Torna inteiros (ex.: 0.5/0.25 → 50/25) para poder dividir pelo MDC
    escala = 10 ** max(_decimal_places(num_text), _decimal_places(den_text))
    numerador = int(round(numerador_f * escala))
    denominador = int(round(denominador_f * escala))

    mdc = math.gcd(numerador, denominador)
    num_final, den_final = numerador // mdc, denominador // mdc

    steps = [
        f"MDC({abs(numerador)}, {abs(denominador)}) = {mdc}",
        f"{numerador} ÷ {mdc} = {num_final}  |  {denominador} ÷ {mdc} = {den_final}",
    ]
    if mdc == 1:
        steps.append("A fração já estava irreduzível (MDC = 1).")

    resultado = Fraction(num_final, den_final)
    display = f"{numerador}/{denominador} = {num_final}/{den_final}" if den_final != 1 else f"{numerador}/{denominador} = {num_final}"
    display += f" ≈ {fmt(float(resultado))}" if den_final != 1 else ""
    return {"display": display, "steps": steps}


@op(
    "frac.decimal_para_fracao",
    "fracoes",
    "Decimal para fração",
    "Converte um número decimal (ou misto) na sua forma de fração irredutível.",
    [
        {"name": "value", "label": "Número", "type": "fraction", "placeholder": "ex: 0.75 ou 2 1/4"},
    ],
    order=6,
)
def decimal_para_fracao(value: Fraction):
    casas = decimal_places(value)
    steps = [f"Valor recebido: {fmt(float(value))}"]
    if value.denominator == 1:
        steps.append("O número é inteiro — a fração é o próprio inteiro sobre 1.")
    elif is_terminating_decimal(value):
        steps.append(f"Com {casas} casa(s) decimal(is), multiplicar por 10^{casas} e simplificar.")
        steps.append(f"Simplificando pelo MDC: {_show(value)}")
    else:
        steps.append(f"O decimal não termina → fração irredutível: {_show(value)}")
    return {"display": f"{fmt(float(value))} = {_show(value)}", "steps": steps}


@op(
    "frac.para_decimal",
    "fracoes",
    "Fração para decimal",
    "Converte uma fração em número decimal.",
    [
        {"name": "a", "label": "Fração", "type": "fraction", "placeholder": "ex: 5/8"},
    ],
    order=7,
)
def frac_para_decimal(a: Fraction):
    decimal = float(a)
    steps = [
        f"{a.numerator} ÷ {a.denominator} = {fmt(decimal)}",
        "Se o decimal termina, a fração tem como denominador apenas os fatores 2 e 5.",
    ]
    return {"display": f"{_show(a)} = {fmt(decimal)}", "steps": steps}


@op(
    "frac.misto",
    "fracoes",
    "Número misto → fração",
    "Transforma um número misto (ex.: 2 3/4) numa fração imprópria.",
    [
        {"name": "value", "label": "Número misto", "type": "fraction", "placeholder": "ex: 2 3/4"},
    ],
    order=8,
)
def frac_misto(value: Fraction):
    inteiro = value.numerator // value.denominator
    resto = value.numerator % value.denominator
    steps = [
        f"Parte inteira: {inteiro}",
        f"{inteiro} × {value.denominator} + {resto} = {value.numerator}",
        f"Fração imprópria: {_show(value)}",
    ]
    if resto == 0:
        steps.append("O número é inteiro — não há parte fracionária.")
        display = f"{inteiro} = {_show(value)}"
    else:
        parte_fracionaria = Fraction(resto, value.denominator)
        display = f"{inteiro} + {_show(parte_fracionaria)} = {_show(value)}"
    return {"display": display, "steps": steps}
