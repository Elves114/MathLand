"""Operações de álgebra: equações, sistemas e funções."""

import math

from ops.helpers import OpError, fmt, safe_eval
from ops.registry import op


def _linear_left(a, b):
    """Representa 'a·x + b' de forma amigável: 2x + 3, x - 4, 5..."""
    if a == 0:
        return fmt(b)
    if a == 1:
        termo = "x"
    elif a == -1:
        termo = "−x"
    else:
        termo = f"{fmt(a)}x"
    if b == 0:
        return termo
    return f"{termo} + {fmt(b)}" if b > 0 else f"{termo} − {fmt(-b)}"


@op(
    "alg.linear",
    "algebra",
    "Equação do 1.º grau",
    "Resolve equações do tipo a·x + b = c.",
    [
        {"name": "a", "label": "a (coeficiente de x)", "type": "number", "placeholder": "ex: 2"},
        {"name": "b", "label": "b (termo independente)", "type": "number", "placeholder": "ex: 4"},
        {"name": "c", "label": "c (resultado)", "type": "number", "placeholder": "ex: 10"},
    ],
    order=1,
)
def equacao_linear(a, b, c):
    if a == 0:
        if b == c:
            raise OpError("A equação tem infinitas soluções (0 = 0).")
        raise OpError("A equação não tem solução (a = 0 e b ≠ c).")
    x = (c - b) / a
    return {
        "display": f"{_linear_left(a, b)} = {fmt(c)}  →  x = {fmt(x)}",
        "steps": [
            f"Mover o termo independente: {fmt(a)}x = {fmt(c)} − {fmt(b)} = {fmt(c - b)}",
            f"Dividir por {fmt(a)}: x = {fmt(c - b)} ÷ {fmt(a)} = {fmt(x)}",
        ],
        "details": [{"label": "Solução", "value": f"x = {fmt(x)}"}],
    }


@op(
    "alg.quadratica",
    "algebra",
    "Equação do 2.º grau",
    "Resolve a·x² + b·x + c = 0 pela fórmula de Bhaskara.",
    [
        {"name": "a", "label": "a", "type": "number", "placeholder": "ex: 1"},
        {"name": "b", "label": "b", "type": "number", "placeholder": "ex: -5"},
        {"name": "c", "label": "c", "type": "number", "placeholder": "ex: 6"},
    ],
    order=2,
)
def equacao_quadratica(a, b, c):
    if a == 0:
        raise OpError("Com a = 0 a equação é do 1.º grau. Use a equação do 1.º grau.")

    delta = b * b - 4 * a * c
    steps = [f"Δ = b² − 4ac = ({fmt(b)})² − 4({fmt(a)})({fmt(c)}) = {fmt(delta)}"]

    if delta > 0:
        raiz_delta = math.sqrt(delta)
        x1 = (-b - raiz_delta) / (2 * a)
        x2 = (-b + raiz_delta) / (2 * a)
        x1, x2 = sorted([x1, x2])
        steps += [
            f"√Δ = √{fmt(delta)} = {fmt(raiz_delta)}",
            f"x₁ = ({fmt(-b)} − {fmt(raiz_delta)}) ÷ {fmt(2 * a)} = {fmt(x1)}",
            f"x₂ = ({fmt(-b)} + {fmt(raiz_delta)}) ÷ {fmt(2 * a)} = {fmt(x2)}",
        ]
        display = f"Duas soluções reais: x₁ = {fmt(x1)}  |  x₂ = {fmt(x2)}"
        details = [{"label": "x₁", "value": fmt(x1)}, {"label": "x₂", "value": fmt(x2)}]
    elif delta == 0:
        x = -b / (2 * a)
        steps.append(f"x = −b ÷ 2a = {fmt(-b)} ÷ {fmt(2 * a)} = {fmt(x)} (raiz dupla)")
        display = f"Uma solução dupla: x = {fmt(x)}"
        details = [{"label": "x (raiz dupla)", "value": fmt(x)}]
    else:
        parte_real = fmt(-b / (2 * a))
        parte_imag = fmt(math.sqrt(abs(delta)) / (2 * a))
        steps += [
            f"Δ < 0 → não existem raízes reais.",
            f"Em números complexos: x = {parte_real} ± {parte_imag}i",
        ]
        display = f"Sem raízes reais (Δ = {fmt(delta)}). Complexas: {parte_real} ± {parte_imag}i"
        details = [
            {"label": "Parte real", "value": parte_real},
            {"label": "Parte imaginária", "value": f"± {parte_imag}i"},
        ]

    if delta >= 0:  # só faz sentido verificar a soma das raízes reais
        steps.append(f"Verificação com a soma: x₁ + x₂ = {fmt(-b / a)} = −b/a ✓")
    return {"display": display, "steps": steps, "details": details}


@op(
    "alg.sistema",
    "algebra",
    "Sistema 2×2",
    "Resolve um sistema de duas equações com duas incógnitas (Regra de Cramer).",
    [
        {"name": "a1", "label": "a₁ (1.ª eq.: a₁x + b₁y = c₁)", "type": "number", "placeholder": "ex: 1"},
        {"name": "b1", "label": "b₁", "type": "number", "placeholder": "ex: 1"},
        {"name": "c1", "label": "c₁", "type": "number", "placeholder": "ex: 5"},
        {"name": "a2", "label": "a₂ (2.ª eq.: a₂x + b₂y = c₂)", "type": "number", "placeholder": "ex: 2"},
        {"name": "b2", "label": "b₂", "type": "number", "placeholder": "ex: -1"},
        {"name": "c2", "label": "c₂", "type": "number", "placeholder": "ex: 1"},
    ],
    order=3,
)
def sistema_2x2(a1, b1, c1, a2, b2, c2):
    det = a1 * b2 - a2 * b1
    if abs(det) < 1e-12:
        # Determinante zero: sistema sem solução única
        if abs(a1 * c2 - a2 * c1) < 1e-12 and abs(b1 * c2 - b2 * c1) < 1e-12:
            raise OpError("O sistema tem infinitas soluções (equações dependentes).")
        raise OpError("O sistema não tem solução (equações paralelas / incompatíveis).")

    x = (c1 * b2 - c2 * b1) / det
    y = (a1 * c2 - a2 * c1) / det
    return {
        "display": f"x = {fmt(x)}  |  y = {fmt(y)}",
        "steps": [
            f"Determinante: Δ = ({fmt(a1)})({fmt(b2)}) − ({fmt(a2)})({fmt(b1)}) = {fmt(det)}",
            f"x = (c₁b₂ − c₂b₁) ÷ Δ = {fmt(c1 * b2 - c2 * b1)} ÷ {fmt(det)} = {fmt(x)}",
            f"y = (a₁c₂ − a₂c₁) ÷ Δ = {fmt(a1 * c2 - a2 * c1)} ÷ {fmt(det)} = {fmt(y)}",
        ],
        "details": [{"label": "x", "value": fmt(x)}, {"label": "y", "value": fmt(y)}],
    }


@op(
    "alg.funcao",
    "algebra",
    "Calcular f(x)",
    "Substitui um valor de x numa expressão (ex.: x² + 3x − 5 com x = 4).",
    [
        {
            "name": "expression",
            "label": "Expressão com x",
            "type": "expression",
            "placeholder": "ex: x^2 + 3*x - 5",
            "hint": "Aceita: ^ potências, 2x, sqrt(), log(), pi...",
        },
        {"name": "x", "label": "Valor de x", "type": "number", "placeholder": "ex: 4"},
    ],
    order=4,
)
def calcular_funcao(expression, x):
    valor = safe_eval(expression, {"x": x})
    steps = [
        f"Substituir x = {fmt(x)} na expressão: {expression.strip()}",
        f"f({fmt(x)}) = {fmt(valor)}",
    ]
    return {
        "display": f"f({fmt(x)}) = {fmt(valor)}",
        "steps": steps,
        "details": [{"label": f"f({fmt(x)})", "value": fmt(valor)}],
    }
