"""Funções auxiliares: validação de entrada, formatação e avaliador seguro."""

import ast
import math
import operator
import re
from decimal import Decimal
from fractions import Fraction


class OpError(Exception):
    """Erro de validação/cálculo com mensagem amigável (em português)."""


# ---------------------------------------------------------------- conversão


def to_number(value, label="valor"):
    """Converte texto do utilizador em float (aceita vírgula decimal e frações)."""
    if isinstance(value, bool):
        raise OpError(f"'{label}' deve ser um número.")
    if isinstance(value, (int, float)):
        return float(value)

    text = str(value).strip().replace(",", ".")
    if not text:
        raise OpError(f"O campo '{label}' não pode estar vazio.")

    if "/" in text:
        return float(parse_fraction(text, label))

    try:
        return float(text)
    except ValueError:
        raise OpError(f"'{value}' não é um número válido para '{label}'.")


def to_int(value, label="valor"):
    """Converte texto do utilizador em inteiro."""
    number = to_number(value, label)
    if abs(number - round(number)) > 1e-9:
        raise OpError(f"'{label}' deve ser um número inteiro (recebido: {value}).")
    return int(round(number))


def parse_list(value, label="lista"):
    """Converte '1, 2, 3' numa lista de floats."""
    if isinstance(value, (list, tuple)):
        items = list(value)
    else:
        text = str(value).strip()
        if not text:
            raise OpError(f"O campo '{label}' não pode estar vazio.")
        items = [part for part in re.split(r"[,;\s]+", text) if part]

    if not items:
        raise OpError(f"O campo '{label}' não pode estar vazio.")

    numbers = []
    for index, item in enumerate(items, start=1):
        numbers.append(to_number(item, f"{label} (valor {index})"))
    return numbers


def parse_fraction(value, label="fração"):
    """Converte '3/4', '0.75' ou '1 1/2' em Fraction."""
    if isinstance(value, Fraction):
        return value
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return Fraction(str(value)).limit_denominator(10**12)

    text = str(value).strip().replace(",", ".")
    if not text:
        raise OpError(f"O campo '{label}' não pode estar vazio.")

    parts = text.split()
    if len(parts) == 2:  # número misto: "1 1/2"
        whole = to_number(parts[0], label)
        if abs(whole - round(whole)) > 1e-9:
            raise OpError(f"Número misto inválido em '{label}': {value}.")
        return Fraction(int(round(whole))) + parse_fraction(parts[1], label)

    if "/" in text:
        numerator, _, denominator = text.partition("/")
        if not denominator.strip():
            raise OpError(f"Fração inválida em '{label}': {value}.")
        try:
            return Fraction(f"{numerator.strip()}/{denominator.strip()}")
        except ZeroDivisionError:
            # Fraction("1/0") lança ZeroDivisionError — mensagem própria para o utilizador
            raise OpError(f"O denominador de '{label}' não pode ser zero.")
        except ValueError:
            raise OpError(f"Fração inválida em '{label}': {value}.")

    try:
        return Fraction(text)
    except ValueError:
        raise OpError(f"'{value}' não é uma fração válida para '{label}'.")


def is_terminating_decimal(value) -> bool:
    """True se a fração tem expansão decimal finita (denominador só com 2 e 5)."""
    if not isinstance(value, Fraction):
        return True
    resto = value.denominator
    while resto % 2 == 0:
        resto //= 2
    while resto % 5 == 0:
        resto //= 5
    return resto == 1


def decimal_places(value):
    """Número de casas decimais de um valor (inteiro → 0).

    Usa `Decimal(str(...))` para não ser enganada por notação científica:
    `str(1e-05)` é `"1e-05"` (sem ponto) e teria dado 0 casas em vez de 5.
    """
    if isinstance(value, bool):
        return 0
    if isinstance(value, int):  # inteiros (e bool já tratado) → 0 casas
        return 0
    if isinstance(value, float) and value.is_integer():
        return 0  # 48.0 não precisa de casas decimais

    if isinstance(value, Fraction):
        if value.denominator == 1:
            return 0
        if not is_terminating_decimal(value):
            value = float(value)  # decimal infinito → cai para a aproximação em float
        else:
            resto = value.denominator
            fatores_2 = fatores_5 = 0
            while resto % 2 == 0:
                resto //= 2
                fatores_2 += 1
            while resto % 5 == 0:
                resto //= 5
                fatores_5 += 1
            return max(fatores_2, fatores_5)

    try:
        exponent = Decimal(str(float(value))).as_tuple().exponent
    except (ValueError, OverflowError):
        return 0
    return max(0, -exponent) if isinstance(exponent, int) else 0


def coerce_field(field, raw):
    """Converte o valor cru vindo do frontend para o tipo esperado pelo campo."""
    field_type = field.get("type", "text")
    label = field.get("label", field.get("name", "campo"))
    required = field.get("required", True)

    if not str(raw if raw is not None else "").strip() and not required:
        return None

    if field_type == "number":
        return to_number(raw, label)
    if field_type == "integer":
        return to_int(raw, label)
    if field_type == "list":
        return parse_list(raw, label)
    if field_type == "fraction":
        return parse_fraction(raw, label)
    if field_type == "select":
        value = str(raw).strip()
        options = [str(option.get("value")) for option in field.get("options", [])]
        if options and value not in options:
            raise OpError(f"Opção inválida para '{label}'.")
        return value

    text = str(raw if raw is not None else "").strip()
    if required and not text:
        raise OpError(f"O campo '{label}' é obrigatório.")
    return text


# -------------------------------------------------------- validação de domínio


def ensure_positive(value, label):
    """Exige value > 0 (medidas, contagens, ...)."""
    if value <= 0:
        raise OpError(f"'{label}' deve ser um número positivo (recebido: {fmt(value)}).")


def ensure_non_negative(value, label):
    """Exige value ≥ 0 (capitais, tempos, ...)."""
    if value < 0:
        raise OpError(f"'{label}' não pode ser negativo (recebido: {fmt(value)}).")


def ensure_between(value, low, high, label):
    """Exige low ≤ value ≤ high."""
    if value < low or value > high:
        raise OpError(
            f"'{label}' tem de estar entre {fmt(low)} e {fmt(high)} (recebido: {fmt(value)})."
        )


# ------------------------------------------------------------- formatação


def fmt(value):
    """Formata um número para exibição amigável."""
    if isinstance(value, Fraction):
        if value.denominator == 1:
            return str(value.numerator)
        return f"{value.numerator}/{value.denominator}"

    if isinstance(value, bool):
        return str(value)

    if isinstance(value, int):
        return str(value)

    if isinstance(value, float):
        if math.isnan(value):
            return "NaN"
        if math.isinf(value):
            return "∞" if value > 0 else "-∞"
        if value == 0:
            return "0"
        if abs(value - round(value)) < 1e-12 and abs(value) < 1e16:
            return str(int(round(value)))
        rounded = round(value, 6)
        if abs(rounded) >= 1e-6:
            return f"{rounded:.6f}".rstrip("0").rstrip(".")
        return f"{value:.6g}"

    return str(value)


# ------------------------------------------------------- avaliador de expressões

_BIN_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_UNARY_OPS = {ast.UAdd: operator.pos, ast.USub: operator.neg}
_FUNCTIONS = {
    "sqrt": math.sqrt,
    "abs": abs,
    "round": round,
    "min": min,
    "max": max,
    "pow": pow,
    "log": math.log,
    "log10": math.log10,
    "log2": math.log2,
    "exp": math.exp,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "floor": math.floor,
    "ceil": math.ceil,
    "factorial": math.factorial,
}
_CONSTANTS = {"pi": math.pi, "e": math.e, "tau": math.tau}


def _preprocess(expression):
    """Suporta '^' como potência e multiplicação implícita: 2x, 2(x+1)."""
    expr = expression.replace("^", "**")
    expr = re.sub(r"(?<=\d)(?=[a-zA-Z(])", "*", expr)
    expr = re.sub(r"(?<=\))(?=[\da-zA-Z(])", "*", expr)
    return expr


def safe_eval(expression, names=None):
    """Avalia uma expressão matemática de forma segura (sem execução de código)."""
    variables = dict(names or {})
    expr = _preprocess(str(expression))
    if not expr.strip():
        raise OpError("A expressão não pode estar vazia.")

    try:
        tree = ast.parse(expr, mode="eval")
    except SyntaxError:
        raise OpError(f"Expressão inválida: {expression}")

    try:
        return _eval_node(tree.body, variables)
    except OpError:
        raise
    except ZeroDivisionError:
        raise OpError("Divisão por zero na expressão.")
    except (OverflowError, ValueError) as exc:
        raise OpError(f"Não foi possível calcular a expressão ({exc}).")


def _eval_node(node, names):
    if isinstance(node, ast.Constant):
        if isinstance(node.value, bool) or not isinstance(node.value, (int, float)):
            raise OpError("Só são permitidos números na expressão.")
        return node.value

    if isinstance(node, ast.Name):
        if node.id in names:
            return names[node.id]
        if node.id in _CONSTANTS:
            return _CONSTANTS[node.id]
        raise OpError(f"Variável ou símbolo desconhecido: '{node.id}'.")

    if isinstance(node, ast.BinOp):
        func = _BIN_OPS.get(type(node.op))
        if func is None:
            raise OpError("Operador não suportado na expressão.")
        left = _eval_node(node.left, names)
        right = _eval_node(node.right, names)
        if isinstance(node.op, ast.Pow):
            if abs(right) > 10000:
                raise OpError("Expoente demasiado grande.")
            if abs(left) > 1 and abs(right) > 500:
                raise OpError("Resultado demasiado grande.")
        try:
            return func(left, right)
        except ZeroDivisionError:
            raise OpError("Divisão por zero na expressão.")

    if isinstance(node, ast.UnaryOp):
        func = _UNARY_OPS.get(type(node.op))
        if func is None:
            raise OpError("Operador não suportado na expressão.")
        return func(_eval_node(node.operand, names))

    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise OpError("Chamada de função não suportada.")
        name = node.func.id
        if name not in _FUNCTIONS:
            raise OpError(f"Função desconhecida: '{name}'. (disponíveis: {', '.join(sorted(_FUNCTIONS))})")
        if node.keywords:
            raise OpError("Argumentos nomeados não são permitidos.")
        args = [_eval_node(arg, names) for arg in node.args]
        try:
            return _FUNCTIONS[name](*args)
        except ZeroDivisionError:
            raise OpError("Divisão por zero na expressão.")

    raise OpError("Trecho da expressão não suportado.")
