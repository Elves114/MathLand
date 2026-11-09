"""Operações de trigonometria: funções, triângulo retângulo e lei dos senos."""

import math

from ops.helpers import OpError, fmt
from ops.registry import op

FUNCOES = {"sen": math.sin, "cos": math.cos, "tan": math.tan}

# Valores exatos de referência (em graus) para os ângulos mais usados
VALORES_EXATOS = {
    0: {"sen": "0", "cos": "1", "tan": "0"},
    30: {"sen": "1/2", "cos": "√3/2", "tan": "√3/3"},
    45: {"sen": "√2/2", "cos": "√2/2", "tan": "1"},
    60: {"sen": "√3/2", "cos": "1/2", "tan": "√3"},
    90: {"sen": "1", "cos": "0"},
}


def _suaviza(valor):
    """Elimina o ruído de ponto flutuante (sen(180°) ≈ 1.2e-16 → 0)."""
    if abs(valor) < 1e-12:
        return 0.0
    inteiro = round(valor)
    if abs(valor - inteiro) < 1e-12:
        return float(inteiro)
    return valor


def _para_radianos(angulo, unidade):
    if unidade == "graus":
        return math.radians(angulo)
    if unidade == "radianos":
        return float(angulo)
    raise OpError("Unidade inválida — use 'graus' ou 'radianos'.")


@op(
    "trig.funcao",
    "trigonometria",
    "Seno, cosseno e tangente",
    "Calcula a função trigonométrica de um ângulo (graus ou radianos).",
    [
        {
            "name": "funcao",
            "label": "Função",
            "type": "select",
            "options": [
                {"value": "sen", "label": "sen — seno"},
                {"value": "cos", "label": "cos — cosseno"},
                {"value": "tan", "label": "tan — tangente"},
            ],
        },
        {"name": "angulo", "label": "Ângulo", "type": "number", "placeholder": "ex: 30"},
        {
            "name": "unidade",
            "label": "Unidade do ângulo",
            "type": "select",
            "options": [
                {"value": "graus", "label": "Graus (°)"},
                {"value": "radianos", "label": "Radianos"},
            ],
        },
    ],
    order=1,
)
def funcao_trigonometrica(funcao, angulo, unidade):
    if funcao not in FUNCOES:
        raise OpError(f"Função inválida: {funcao}.")
    rad = _para_radianos(angulo, unidade)

    if funcao == "tan" and abs(math.cos(rad)) < 1e-12:
        raise OpError(
            f"A tangente não está definida para {fmt(angulo)} {unidade} "
            "(o cosseno é zero — ângulo de 90° + k·180°)."
        )

    valor = _suaviza(FUNCOES[funcao](rad))
    sufixo = "°" if unidade == "graus" else ""
    steps = []
    if unidade == "graus":
        steps.append(f"Converter para radianos: {fmt(angulo)}° × π ÷ 180 = {fmt(rad)} rad")
    steps.append(f"{funcao}({fmt(rad)} rad) = {fmt(valor)}")

    exato = VALORES_EXATOS.get(angulo, {}).get(funcao)
    if unidade == "graus" and exato:
        steps.append(f"Ângulo de referência: {funcao}({fmt(angulo)}°) = {exato}")

    return {
        "display": f"{funcao}({fmt(angulo)}{sufixo}) = {fmt(valor)}",
        "steps": steps,
        "details": [
            {"label": "Ângulo em radianos", "value": fmt(rad)},
            {"label": f"{funcao}({fmt(angulo)}{sufixo})", "value": fmt(valor)},
        ],
    }


@op(
    "trig.retangulo",
    "trigonometria",
    "Triângulo retângulo",
    "Conhece a hipotenusa e um ângulo agudo → calcula os dois catetos.",
    [
        {"name": "hipotenusa", "label": "Hipotenusa (c)", "type": "number", "placeholder": "ex: 10"},
        {"name": "angulo", "label": "Ângulo agudo (graus)", "type": "number", "placeholder": "ex: 30"},
    ],
    order=2,
)
def triangulo_retangulo(hipotenusa, angulo):
    if hipotenusa <= 0:
        raise OpError("A hipotenusa tem de ser um número positivo.")
    if not 0 < angulo < 90:
        raise OpError("O ângulo tem de estar entre 0° e 90° (exclusivo).")

    rad = math.radians(angulo)
    seno = math.sin(rad)
    cosseno = math.cos(rad)
    oposto = _suaviza(hipotenusa * seno)
    adjacente = _suaviza(hipotenusa * cosseno)
    hipotenusa2 = hipotenusa**2

    steps = [
        f"Cateto oposto = c × sen(A) = {fmt(hipotenusa)} × {fmt(seno)} = {fmt(oposto)}",
        f"Cateto adjacente = c × cos(A) = {fmt(hipotenusa)} × {fmt(cosseno)} = {fmt(adjacente)}",
        f"Verificação (Pitágoras): {fmt(oposto)}² + {fmt(adjacente)}² = "
        f"{fmt(oposto**2 + adjacente**2)} = {fmt(hipotenusa2)} ✓",
    ]

    return {
        "display": f"Cateto oposto = {fmt(oposto)}  |  Cateto adjacente = {fmt(adjacente)}",
        "steps": steps,
        "details": [
            {"label": "Cateto oposto", "value": fmt(oposto)},
            {"label": "Cateto adjacente", "value": fmt(adjacente)},
            {"label": "Ângulo restante", "value": f"{fmt(90 - angulo)}°"},
        ],
    }


@op(
    "trig.lei_senos",
    "trigonometria",
    "Lei dos senos",
    "Dados um lado com o ângulo oposto e um segundo ângulo, encontra os restantes lados do triângulo.",
    [
        {"name": "a", "label": "Lado a", "type": "number", "placeholder": "ex: 8"},
        {"name": "angulo_A", "label": "Ângulo A (oposto a a), em graus", "type": "number", "placeholder": "ex: 60"},
        {"name": "angulo_B", "label": "Ângulo B, em graus", "type": "number", "placeholder": "ex: 45"},
    ],
    order=3,
)
def lei_dos_senos(a, angulo_A, angulo_B):
    if a <= 0:
        raise OpError("O lado tem de ser um número positivo.")
    for nome, angulo in (("A", angulo_A), ("B", angulo_B)):
        if not 0 < angulo < 180:
            raise OpError(f"O ângulo {nome} tem de estar entre 0° e 180°.")
    if angulo_A + angulo_B >= 180:
        raise OpError("A soma dos ângulos A e B tem de ser inferior a 180° (senão não há triângulo).")

    sen_A = math.sin(math.radians(angulo_A))
    sen_B = math.sin(math.radians(angulo_B))
    if abs(sen_A) < 1e-12:
        raise OpError("O seno do ângulo A é zero — a lei dos senos não está definida.")

    b = a * sen_B / sen_A
    angulo_C = 180 - angulo_A - angulo_B
    sen_C = math.sin(math.radians(angulo_C))
    c = a * sen_C / sen_A

    steps = [
        f"Lei dos senos: a ÷ sen(A) = b ÷ sen(B) = c ÷ sen(C)",
        f"b = a × sen(B) ÷ sen(A) = {fmt(a)} × {fmt(sen_B)} ÷ {fmt(sen_A)} = {fmt(b)}",
        f"C = 180° − {fmt(angulo_A)}° − {fmt(angulo_B)}° = {fmt(angulo_C)}°",
        f"c = a × sen(C) ÷ sen(A) = {fmt(a)} × {fmt(sen_C)} ÷ {fmt(sen_A)} = {fmt(c)}",
    ]

    return {
        "display": f"b = {fmt(b)}  |  c = {fmt(c)}  |  C = {fmt(angulo_C)}°",
        "steps": steps,
        "details": [
            {"label": "Lado b", "value": fmt(b)},
            {"label": "Lado c", "value": fmt(c)},
            {"label": "Ângulo C", "value": f"{fmt(angulo_C)}°"},
        ],
    }
