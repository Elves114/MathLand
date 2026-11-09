"""Operações de geometria: áreas, perímetros, volumes e distâncias."""

import math

from ops.helpers import OpError, ensure_positive, fmt
from ops.registry import op


def _positive(values, labels):
    """Valida que todos os valores são positivos (reutiliza helpers.ensure_positive)."""
    for value, label in zip(values, labels):
        ensure_positive(value, label)


@op(
    "geo.retangulo",
    "geometria",
    "Retângulo",
    "Área, perímetro e diagonal de um retângulo.",
    [
        {"name": "base", "label": "Base", "type": "number", "placeholder": "ex: 8"},
        {"name": "altura", "label": "Altura", "type": "number", "placeholder": "ex: 5"},
    ],
    order=1,
)
def retangulo(base, altura):
    _positive([base, altura], ["base", "altura"])
    area = base * altura
    perimetro = 2 * (base + altura)
    diagonal = math.sqrt(base**2 + altura**2)
    return {
        "display": f"Área = {fmt(area)}  |  Perímetro = {fmt(perimetro)}  |  Diagonal = {fmt(diagonal)}",
        "steps": [
            f"A = b × h = {fmt(base)} × {fmt(altura)} = {fmt(area)}",
            f"P = 2 × (b + h) = 2 × {fmt(base + altura)} = {fmt(perimetro)}",
            f"d = √(b² + h²) = √({fmt(base**2)} + {fmt(altura**2)}) = {fmt(diagonal)} (Pitágoras)",
        ],
        "details": [
            {"label": "Área", "value": fmt(area)},
            {"label": "Perímetro", "value": fmt(perimetro)},
            {"label": "Diagonal", "value": fmt(diagonal)},
        ],
    }


@op(
    "geo.quadrado",
    "geometria",
    "Quadrado",
    "Área, perímetro e diagonal de um quadrado.",
    [
        {"name": "lado", "label": "Lado", "type": "number", "placeholder": "ex: 6"},
    ],
    order=2,
)
def quadrado(lado):
    _positive([lado], ["lado"])
    area = lado**2
    perimetro = 4 * lado
    diagonal = lado * math.sqrt(2)
    return {
        "display": f"Área = {fmt(area)}  |  Perímetro = {fmt(perimetro)}  |  Diagonal = {fmt(diagonal)}",
        "steps": [
            f"A = l² = {fmt(lado)}² = {fmt(area)}",
            f"P = 4 × l = 4 × {fmt(lado)} = {fmt(perimetro)}",
            f"d = l√2 = {fmt(lado)} × √2 = {fmt(diagonal)}",
        ],
        "details": [
            {"label": "Área", "value": fmt(area)},
            {"label": "Perímetro", "value": fmt(perimetro)},
            {"label": "Diagonal", "value": fmt(diagonal)},
        ],
    }


@op(
    "geo.triangulo_area",
    "geometria",
    "Triângulo (base e altura)",
    "Área de um triângulo conhecendo a base e a altura.",
    [
        {"name": "base", "label": "Base", "type": "number", "placeholder": "ex: 10"},
        {"name": "altura", "label": "Altura", "type": "number", "placeholder": "ex: 6"},
    ],
    order=3,
)
def triangulo_area(base, altura):
    _positive([base, altura], ["base", "altura"])
    area = base * altura / 2
    return {
        "display": f"Área = {fmt(area)}",
        "steps": [f"A = (b × h) ÷ 2 = ({fmt(base)} × {fmt(altura)}) ÷ 2 = {fmt(area)}"],
        "details": [{"label": "Área", "value": fmt(area)}],
    }


@op(
    "geo.triangulo_lados",
    "geometria",
    "Triângulo (3 lados)",
    "Perímetro e área de um triângulo conhecendo os três lados (fórmula de Heron).",
    [
        {"name": "a", "label": "Lado a", "type": "number", "placeholder": "ex: 7"},
        {"name": "b", "label": "Lado b", "type": "number", "placeholder": "ex: 8"},
        {"name": "c", "label": "Lado c", "type": "number", "placeholder": "ex: 9"},
    ],
    order=4,
)
def triangulo_lados(a, b, c):
    _positive([a, b, c], ["lado a", "lado b", "lado c"])
    if a + b <= c or a + c <= b or b + c <= a:
        raise OpError(
            "Estas medidas não formam um triângulo: a soma de dois lados deve ser sempre maior que o terceiro."
        )
    perimetro = a + b + c
    s = perimetro / 2
    area = math.sqrt(s * (s - a) * (s - b) * (s - c))
    return {
        "display": f"Área = {fmt(area)}  |  Perímetro = {fmt(perimetro)}",
        "steps": [
            f"P = a + b + c = {fmt(perimetro)}",
            f"Semiperímetro: s = P ÷ 2 = {fmt(s)}",
            f"A = √(s(s−a)(s−b)(s−c)) = √({fmt(s)} × {fmt(s - a)} × {fmt(s - b)} × {fmt(s - c)}) = {fmt(area)}",
        ],
        "details": [{"label": "Área (Heron)", "value": fmt(area)}, {"label": "Perímetro", "value": fmt(perimetro)}],
    }


@op(
    "geo.circulo",
    "geometria",
    "Círculo",
    "Diâmetro, área e comprimento (circunferência) de um círculo.",
    [
        {"name": "raio", "label": "Raio", "type": "number", "placeholder": "ex: 5"},
    ],
    order=5,
)
def circulo(raio):
    _positive([raio], ["raio"])
    diametro = 2 * raio
    area = math.pi * raio**2
    perimetro = 2 * math.pi * raio
    return {
        "display": f"Área = {fmt(area)}  |  Comprimento = {fmt(perimetro)}  |  Diâmetro = {fmt(diametro)}",
        "steps": [
            f"π ≈ {fmt(math.pi)}",
            f"d = 2r = {fmt(diametro)}",
            f"A = πr² = π × {fmt(raio**2)} = {fmt(area)}",
            f"C = 2πr = 2π × {fmt(raio)} = {fmt(perimetro)}",
        ],
        "details": [
            {"label": "Diâmetro", "value": fmt(diametro)},
            {"label": "Área", "value": fmt(area)},
            {"label": "Comprimento", "value": fmt(perimetro)},
        ],
    }


@op(
    "geo.trapezio",
    "geometria",
    "Trapézio",
    "Área de um trapézio conhecendo as duas bases e a altura.",
    [
        {"name": "base1", "label": "Base maior (B)", "type": "number", "placeholder": "ex: 12"},
        {"name": "base2", "label": "Base menor (b)", "type": "number", "placeholder": "ex: 7"},
        {"name": "altura", "label": "Altura (h)", "type": "number", "placeholder": "ex: 5"},
    ],
    order=6,
)
def trapezio(base1, base2, altura):
    _positive([base1, base2, altura], ["base maior", "base menor", "altura"])
    area = (base1 + base2) * altura / 2
    return {
        "display": f"Área = {fmt(area)}",
        "steps": [
            f"A = (B + b) × h ÷ 2",
            f"A = ({fmt(base1)} + {fmt(base2)}) × {fmt(altura)} ÷ 2 = {fmt(area)}",
        ],
        "details": [{"label": "Área", "value": fmt(area)}],
    }


@op(
    "geo.losango",
    "geometria",
    "Losango",
    "Área de um losango pelas diagonais (e perímetro, se indicar o lado).",
    [
        {"name": "d1", "label": "Diagonal 1", "type": "number", "placeholder": "ex: 10"},
        {"name": "d2", "label": "Diagonal 2", "type": "number", "placeholder": "ex: 6"},
        {"name": "lado", "label": "Lado (opcional)", "type": "number", "placeholder": "ex: 5", "required": False},
    ],
    order=7,
)
def losango(d1, d2, lado=None):
    _positive([d1, d2], ["diagonal 1", "diagonal 2"])
    area = d1 * d2 / 2
    steps = [f"A = (d₁ × d₂) ÷ 2 = ({fmt(d1)} × {fmt(d2)}) ÷ 2 = {fmt(area)}"]
    details = [{"label": "Área", "value": fmt(area)}]
    display = f"Área = {fmt(area)}"
    if lado is not None:
        _positive([lado], ["lado"])
        perimetro = 4 * lado
        steps.append(f"P = 4 × l = 4 × {fmt(lado)} = {fmt(perimetro)}")
        details.append({"label": "Perímetro", "value": fmt(perimetro)})
        display += f"  |  Perímetro = {fmt(perimetro)}"
    return {"display": display, "steps": steps, "details": details}


@op(
    "geo.paralelogramo",
    "geometria",
    "Paralelogramo",
    "Área de um paralelogramo (base × altura).",
    [
        {"name": "base", "label": "Base", "type": "number", "placeholder": "ex: 10"},
        {"name": "altura", "label": "Altura", "type": "number", "placeholder": "ex: 6"},
        {"name": "lado", "label": "Lado (opcional, para o perímetro)", "type": "number", "placeholder": "ex: 7", "required": False},
    ],
    order=8,
)
def paralelogramo(base, altura, lado=None):
    _positive([base, altura], ["base", "altura"])
    area = base * altura
    steps = [f"A = b × h = {fmt(base)} × {fmt(altura)} = {fmt(area)}"]
    details = [{"label": "Área", "value": fmt(area)}]
    display = f"Área = {fmt(area)}"
    if lado is not None:
        _positive([lado], ["lado"])
        perimetro = 2 * (base + lado)
        steps.append(f"P = 2 × (b + l) = 2 × {fmt(base + lado)} = {fmt(perimetro)}")
        details.append({"label": "Perímetro", "value": fmt(perimetro)})
        display += f"  |  Perímetro = {fmt(perimetro)}"
    return {"display": display, "steps": steps, "details": details}


@op(
    "geo.pitagoras",
    "geometria",
    "Teorema de Pitágoras",
    "Preencha exatamente 2 campos: os dois catetos (para obter a hipotenusa) ou a hipotenusa e um cateto.",
    [
        {"name": "a", "label": "Cateto a", "type": "number", "placeholder": "ex: 3", "required": False},
        {"name": "b", "label": "Cateto b", "type": "number", "placeholder": "ex: 4", "required": False},
        {"name": "c", "label": "Hipotenusa c", "type": "number", "placeholder": "ex: 5", "required": False},
    ],
    order=9,
)
def pitagoras(a, b, c=None):
    campos = {"a": a, "b": b, "c": c}
    preenchidos = [nome for nome, valor in campos.items() if valor is not None]
    if len(preenchidos) != 2:
        raise OpError("Preencha exatamente dois dos três campos (cateto, cateto e hipotenusa).")

    if c is None:  # hipotenusa em falta
        _positive([a, b], ["cateto a", "cateto b"])
        hipotenusa = math.sqrt(a**2 + b**2)
        return {
            "display": f"c = √(a² + b²) = √({fmt(a**2)} + {fmt(b**2)}) = {fmt(hipotenusa)}",
            "steps": [
                f"c² = a² + b² = {fmt(a)}² + {fmt(b)}² = {fmt(a**2 + b**2)}",
                f"c = √{fmt(a**2 + b**2)} = {fmt(hipotenusa)}",
            ],
            "details": [{"label": "Hipotenusa (c)", "value": fmt(hipotenusa)}],
        }

    _positive([c], ["hipotenusa c"])
    if a is None:  # cateto a em falta
        _positive([b], ["cateto b"])
        if c < b:
            raise OpError("A hipotenusa tem de ser maior ou igual a qualquer cateto.")
        cateto = math.sqrt(c**2 - b**2)
        return {
            "display": f"a = √(c² − b²) = √({fmt(c**2)} − {fmt(b**2)}) = {fmt(cateto)}",
            "steps": [f"a² = c² − b² = {fmt(c**2 - b**2)}", f"a = √{fmt(c**2 - b**2)} = {fmt(cateto)}"],
            "details": [{"label": "Cateto (a)", "value": fmt(cateto)}],
        }

    _positive([a], ["cateto a"])
    if c < a:
        raise OpError("A hipotenusa tem de ser maior ou igual a qualquer cateto.")
    cateto = math.sqrt(c**2 - a**2)
    return {
        "display": f"b = √(c² − a²) = √({fmt(c**2)} − {fmt(a**2)}) = {fmt(cateto)}",
        "steps": [f"b² = c² − a² = {fmt(c**2 - a**2)}", f"b = √{fmt(c**2 - a**2)} = {fmt(cateto)}"],
        "details": [{"label": "Cateto (b)", "value": fmt(cateto)}],
    }


@op(
    "geo.distancia",
    "geometria",
    "Distância entre dois pontos",
    "Distância entre P(x₁, y₁) e Q(x₂, y₂) no plano.",
    [
        {"name": "x1", "label": "x₁", "type": "number", "placeholder": "ex: 1"},
        {"name": "y1", "label": "y₁", "type": "number", "placeholder": "ex: 2"},
        {"name": "x2", "label": "x₂", "type": "number", "placeholder": "ex: 4"},
        {"name": "y2", "label": "y₂", "type": "number", "placeholder": "ex: 6"},
    ],
    order=10,
)
def distancia(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    distancia_valor = math.sqrt(dx**2 + dy**2)
    return {
        "display": f"d = {fmt(distancia_valor)}",
        "steps": [
            f"Δx = x₂ − x₁ = {fmt(dx)}",
            f"Δy = y₂ − y₁ = {fmt(dy)}",
            f"d = √(Δx² + Δy²) = √({fmt(dx**2)} + {fmt(dy**2)}) = {fmt(distancia_valor)}",
        ],
        "details": [{"label": "Distância", "value": fmt(distancia_valor)}],
    }


@op(
    "geo.cubo",
    "geometria",
    "Cubo",
    "Volume, área da superfície e diagonal do espaço de um cubo.",
    [
        {"name": "lado", "label": "Aresta", "type": "number", "placeholder": "ex: 3"},
    ],
    order=11,
)
def cubo(lado):
    _positive([lado], ["aresta"])
    volume = lado**3
    superficie = 6 * lado**2
    diagonal = lado * math.sqrt(3)
    return {
        "display": f"Volume = {fmt(volume)}  |  Área superfície = {fmt(superficie)}  |  Diagonal = {fmt(diagonal)}",
        "steps": [
            f"V = a³ = {fmt(lado)}³ = {fmt(volume)}",
            f"A = 6a² = 6 × {fmt(lado**2)} = {fmt(superficie)}",
            f"d = a√3 = {fmt(diagonal)}",
        ],
        "details": [
            {"label": "Volume", "value": fmt(volume)},
            {"label": "Área da superfície", "value": fmt(superficie)},
            {"label": "Diagonal do espaço", "value": fmt(diagonal)},
        ],
    }


@op(
    "geo.cilindro",
    "geometria",
    "Cilindro reto",
    "Volume e áreas do cilindro reto.",
    [
        {"name": "raio", "label": "Raio da base", "type": "number", "placeholder": "ex: 4"},
        {"name": "altura", "label": "Altura", "type": "number", "placeholder": "ex: 10"},
    ],
    order=12,
)
def cilindro(raio, altura):
    _positive([raio, altura], ["raio", "altura"])
    volume = math.pi * raio**2 * altura
    lateral = 2 * math.pi * raio * altura
    total = lateral + 2 * math.pi * raio**2
    return {
        "display": f"Volume = {fmt(volume)}  |  Área lateral = {fmt(lateral)}  |  Área total = {fmt(total)}",
        "steps": [
            f"V = πr²h = π × {fmt(raio**2)} × {fmt(altura)} = {fmt(volume)}",
            f"A_lateral = 2πrh = {fmt(lateral)}",
            f"A_total = 2πr(r + h) = {fmt(total)}",
        ],
        "details": [
            {"label": "Volume", "value": fmt(volume)},
            {"label": "Área lateral", "value": fmt(lateral)},
            {"label": "Área total", "value": fmt(total)},
        ],
    }


@op(
    "geo.cone",
    "geometria",
    "Cone reto",
    "Volume e áreas do cone reto (inclui a geratriz).",
    [
        {"name": "raio", "label": "Raio da base", "type": "number", "placeholder": "ex: 3"},
        {"name": "altura", "label": "Altura", "type": "number", "placeholder": "ex: 4"},
    ],
    order=13,
)
def cone(raio, altura):
    _positive([raio, altura], ["raio", "altura"])
    volume = math.pi * raio**2 * altura / 3
    geratriz = math.sqrt(raio**2 + altura**2)
    lateral = math.pi * raio * geratriz
    total = lateral + math.pi * raio**2
    return {
        "display": f"Volume = {fmt(volume)}  |  Área lateral = {fmt(lateral)}  |  Área total = {fmt(total)}",
        "steps": [
            f"Geratriz: g = √(r² + h²) = √({fmt(raio**2)} + {fmt(altura**2)}) = {fmt(geratriz)} (Pitágoras)",
            f"V = πr²h ÷ 3 = {fmt(volume)}",
            f"A_lateral = πrg = {fmt(lateral)}",
            f"A_total = πr(r + g) = {fmt(total)}",
        ],
        "details": [
            {"label": "Geratriz", "value": fmt(geratriz)},
            {"label": "Volume", "value": fmt(volume)},
            {"label": "Área lateral", "value": fmt(lateral)},
            {"label": "Área total", "value": fmt(total)},
        ],
    }


@op(
    "geo.esfera",
    "geometria",
    "Esfera",
    "Volume e área da superfície de uma esfera.",
    [
        {"name": "raio", "label": "Raio", "type": "number", "placeholder": "ex: 6"},
    ],
    order=14,
)
def esfera(raio):
    _positive([raio], ["raio"])
    volume = 4 / 3 * math.pi * raio**3
    area = 4 * math.pi * raio**2
    return {
        "display": f"Volume = {fmt(volume)}  |  Área = {fmt(area)}",
        "steps": [
            f"V = (4/3)πr³ = (4/3)π × {fmt(raio**3)} = {fmt(volume)}",
            f"A = 4πr² = 4π × {fmt(raio**2)} = {fmt(area)}",
        ],
        "details": [{"label": "Volume", "value": fmt(volume)}, {"label": "Área", "value": fmt(area)}],
    }
