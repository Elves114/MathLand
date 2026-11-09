"""Operações com matrizes (até 3 × 3)."""

from ops.helpers import OpError, fmt
from ops.registry import op


def _ler_matriz(rotulo, *linhas_brutas):
    """Junta as linhas preenchidas e valida que a matriz é retangular."""
    linhas = [list(linha) for linha in linhas_brutas if linha]
    if len(linhas) < 2:
        raise OpError(f"Preencha pelo menos 2 linhas da matriz {rotulo} (ex.: 1, 2).")

    largura = len(linhas[0])
    for indice, linha in enumerate(linhas, start=1):
        if len(linha) != largura:
            raise OpError(
                f"A matriz {rotulo} tem de ser retangular: a linha {indice} tem "
                f"{len(linha)} coluna(s), mas a linha 1 tem {largura}."
            )
    return linhas


def _mostrar(matriz):
    """Representação numa linha: [1 2 ; 3 4]."""
    return "[" + " ; ".join(" ".join(fmt(v) for v in linha) for linha in matriz) + "]"


def _quadrada(matriz):
    if len(matriz) != len(matriz[0]):
        raise OpError(
            f"O determinante só está definido para matrizes quadradas "
            f"(recebida: {len(matriz)} × {len(matriz[0])})."
        )


def _determinante(matriz):
    """Determinante de 2×2 ou 3×3 (as linhas são limitadas pelos campos do formulário)."""
    if len(matriz) == 2:
        (a, b), (c, d) = matriz
        return a * d - b * c

    (a, b, c), (d, e, f), (g, h, i) = matriz
    return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)


@op(
    "mat.determinante",
    "matrizes",
    "Determinante",
    "Determinante de uma matriz 2×2 ou 3×3.",
    [
        {"name": "linha1", "label": "1.ª linha", "type": "list", "placeholder": "ex: 1, 2"},
        {"name": "linha2", "label": "2.ª linha", "type": "list", "placeholder": "ex: 3, 4"},
        {
            "name": "linha3",
            "label": "3.ª linha (opcional)",
            "type": "list",
            "placeholder": "ex: 5, 6",
            "required": False,
        },
    ],
    order=1,
)
def determinante(linha1, linha2, linha3=None):
    matriz = _ler_matriz("A", linha1, linha2, linha3)
    _quadrada(matriz)
    valor = _determinante(matriz)

    if len(matriz) == 2:
        (a, b), (c, d) = matriz
        formula = f"det = ({fmt(a)})({fmt(d)}) − ({fmt(b)})({fmt(c)}) = {fmt(valor)}"
    else:
        formula = (
            "det = a(ei − fh) − b(di − fg) + c(dh − eg) = "
            f"{fmt(valor)}"
        )

    return {
        "display": f"det(A) = {fmt(valor)}",
        "steps": [
            f"A = {_mostrar(matriz)}",
            formula,
            "det = 0 → as linhas são dependentes (matriz singular)."
            if abs(valor) < 1e-12
            else "det ≠ 0 → a matriz é invertível.",
        ],
        "details": [
            {"label": "Matriz A", "value": _mostrar(matriz)},
            {"label": "Determinante", "value": fmt(valor)},
        ],
    }


@op(
    "mat.soma",
    "matrizes",
    "Soma de matrizes",
    "Soma duas matrizes do mesmo tamanho (elemento a elemento).",
    [
        {"name": "a1", "label": "A — 1.ª linha", "type": "list", "placeholder": "ex: 1, 2"},
        {"name": "a2", "label": "A — 2.ª linha", "type": "list", "placeholder": "ex: 3, 4"},
        {
            "name": "a3",
            "label": "A — 3.ª linha (opcional)",
            "type": "list",
            "placeholder": "ex: 5, 6",
            "required": False,
        },
        {"name": "b1", "label": "B — 1.ª linha", "type": "list", "placeholder": "ex: 10, 20"},
        {"name": "b2", "label": "B — 2.ª linha", "type": "list", "placeholder": "ex: 30, 40"},
        {
            "name": "b3",
            "label": "B — 3.ª linha (opcional)",
            "type": "list",
            "placeholder": "ex: 50, 60",
            "required": False,
        },
    ],
    order=2,
)
def soma_matrizes(a1, a2, a3, b1, b2, b3):
    A = _ler_matriz("A", a1, a2, a3)
    B = _ler_matriz("B", b1, b2, b3)

    if len(A) != len(B) or len(A[0]) != len(B[0]):
        raise OpError(
            f"Para somar, as matrizes têm de ter o mesmo tamanho: "
            f"A é {len(A)}×{len(A[0])} e B é {len(B)}×{len(B[0])}."
        )

    C = [
        [A[i][j] + B[i][j] for j in range(len(A[0]))]
        for i in range(len(A))
    ]

    contas = [
        f"Linha {i + 1}: "
        + " ; ".join(
            f"{fmt(A[i][j])} + {fmt(B[i][j])} = {fmt(C[i][j])}"
            for j in range(len(A[0]))
        )
        for i in range(len(A))
    ]

    return {
        "display": _mostrar(C),
        "steps": [
            f"A = {_mostrar(A)}",
            f"B = {_mostrar(B)}",
            *contas,
            f"A + B = {_mostrar(C)}",
        ],
        "details": [
            {"label": "Resultado (A + B)", "value": _mostrar(C)},
            {"label": "Tamanho", "value": f"{len(A)} × {len(A[0])}"},
        ],
    }


@op(
    "mat.multiplicacao",
    "matrizes",
    "Multiplicação de matrizes",
    "Multiplica A × B (o número de colunas de A tem de ser igual ao de linhas de B).",
    [
        {"name": "a1", "label": "A — 1.ª linha", "type": "list", "placeholder": "ex: 1, 2"},
        {"name": "a2", "label": "A — 2.ª linha", "type": "list", "placeholder": "ex: 3, 4"},
        {
            "name": "a3",
            "label": "A — 3.ª linha (opcional)",
            "type": "list",
            "placeholder": "ex: 5, 6",
            "required": False,
        },
        {"name": "b1", "label": "B — 1.ª linha", "type": "list", "placeholder": "ex: 10, 20"},
        {"name": "b2", "label": "B — 2.ª linha", "type": "list", "placeholder": "ex: 30, 40"},
        {
            "name": "b3",
            "label": "B — 3.ª linha (opcional)",
            "type": "list",
            "placeholder": "ex: 50, 60",
            "required": False,
        },
    ],
    order=3,
)
def multiplicacao_matrizes(a1, a2, a3, b1, b2, b3):
    A = _ler_matriz("A", a1, a2, a3)
    B = _ler_matriz("B", b1, b2, b3)

    if len(A[0]) != len(B):
        raise OpError(
            f"Não é possível multiplicar: A tem {len(A[0])} coluna(s) e B tem "
            f"{len(B)} linha(s) — têm de ser iguais."
        )

    linhas, colunas = len(A), len(B[0])
    comum = len(B)
    C = [
        [sum(A[i][k] * B[k][j] for k in range(comum)) for j in range(colunas)]
        for i in range(linhas)
    ]

    contas = [
        f"Linha {i + 1}, coluna {j + 1}: "
        + " + ".join(
            f"{fmt(A[i][k])}×{fmt(B[k][j])}" for k in range(comum)
        )
        + f" = {fmt(C[i][j])}"
        for i in range(linhas)
        for j in range(colunas)
    ]

    return {
        "display": _mostrar(C),
        "steps": [
            f"A = {_mostrar(A)}  ({len(A)}×{len(A[0])})",
            f"B = {_mostrar(B)}  ({len(B)}×{len(B[0])})",
            *contas,
            f"A × B = {_mostrar(C)}",
        ],
        "details": [
            {"label": "Resultado (A × B)", "value": _mostrar(C)},
            {"label": "Tamanho", "value": f"{len(A)} × {len(B[0])}"},
        ],
    }
