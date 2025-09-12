# Er.py
# Validador de tokens con Expresiones Regulares (INFO1148)
# Lee líneas o párrafos, tokeniza y clasifica cada token.

import re
import argparse
from dataclasses import dataclass
from typing import List, Tuple, Dict

# ---------------------- Tokenizador ----------------------
MASTER_TOKEN_RE = re.compile(r"""
    # 1) Cadenas entre comillas (soporta escapes)
    "(?:[^"\\]|\\.)*" | '(?:[^'\\]|\\.)*'
    |
    # 2) Email
    [A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}
    |
    # 3) Hexadecimal
    0[xX][0-9A-Fa-f]+
    |
    # 4) Científico (e.g., -1.2e+3)
    [+-]?\d+(?:\.\d+)?[eE][+-]?\d+
    |
    # 5) Real con punto (e.g., 12.34)
    [+-]?\d+\.\d+
    |
    # 6) Entero
    [+-]?\d+
    |
    # 7) Operadores (multi-char primero)
    \+\+|--|==|!=|<=|>=|&&|\|\||[+\-*/%<>=!]
    |
    # 8) Identificadores
    [A-Za-z_][A-Za-z0-9_]*
    |
    # 9) Cualquier símbolo no-espacio
    \S
""", re.VERBOSE)

def tokenize(text: str) -> List[str]:
    """Divide una línea/párrafo en tokens sin perder símbolos."""
    tokens: List[str] = []
    i = 0
    n = len(text)
    while i < n:
        if text[i].isspace():
            i += 1
            continue
        m = MASTER_TOKEN_RE.match(text, i)
        if m:
            tokens.append(m.group(0))
            i = m.end()
        else:
            tokens.append(text[i])
            i += 1
    return tokens
# --------------------------------------------------------


# ---------------------- Patrones ------------------------
@dataclass
class Pattern:
    name: str
    regex: re.Pattern

def build_patterns() -> List[Pattern]:
    """
    Patrones ampliados para el Taller ER.
    El orden ayuda a resolver solapes (p. ej., PALABRA_RESERVADA antes que IDENTIFIER).
    """
    return [
        # Palabras reservadas
        Pattern("PALABRA_RESERVADA", re.compile(r"^(if|else|while|for|return|break|continue)$")),

        # Identificadores
        Pattern("IDENTIFIER", re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")),

        # Números
        Pattern("INTEGER", re.compile(r"^[+-]?\d+$")),
        Pattern("REAL_NUMBER", re.compile(r"^[+-]?\d+\.\d+$")),
        Pattern("NUMERO_CIENTIFICO", re.compile(r"^[+-]?\d+(?:\.\d+)?[eE][+-]?\d+$")),
        Pattern("NUMERO_HEXADECIMAL", re.compile(r"^0[xX][0-9A-Fa-f]+$")),

        # Correo y contraseña simple
        Pattern("EMAIL", re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")),
        Pattern("PASSWORD_SIMPLE", re.compile(r"^[A-Za-z0-9]{6,}$")),

        # Operadores
        Pattern("INCREMENTADOR", re.compile(r"^(\+\+|--)$")),
        Pattern("OPERADOR_RELACIONAL", re.compile(r"^(==|!=|<=|>=|<|>)$")),
        Pattern("OPERADOR_LOGICO", re.compile(r"^(&&|\|\||!)$")),
        Pattern("OPERADOR_ARITMETICO", re.compile(r"^(\+|-|\*|/|%)$")),

        # Literales
        Pattern("CADENA_TEXTO", re.compile(r"^(\"([^\"\\]|\\.)*\"|'([^'\\]|\\.)*')$")),
        Pattern("BOOLEANO", re.compile(r"^(true|false|True|False)$")),
    ]
# --------------------------------------------------------


# ------------------ Clasificación & salida ---------------
def classify(s: str, patterns: List[Pattern]) -> Tuple[str, bool]:
    """Devuelve (token_name, valida?)."""
    for p in patterns:
        if p.regex.fullmatch(s):
            return p.name, True
    return "NO_COINCIDE", False

def print_table(rows: List[Tuple[int, str, str, bool]]) -> None:
    """rows: (n_linea, token, token_name, ok)"""
    col1, col2, col3, col4 = "Línea", "Token", "Tipo", "¿Válida?"
    w1 = max(len(col1), 5)
    w2 = max(len(col2), 30)
    w3 = max(len(col3), 18)
    w4 = max(len(col4), 7)

    header = f"{col1:<{w1}} | {col2:<{w2}} | {col3:<{w3}} | {col4:<{w4}}"
    sep = "-" * len(header)
    print(header)
    print(sep)
    for n, tok, token_name, ok in rows:
        val = "Sí" if ok else "No"
        show = tok if len(tok) <= w2 else tok[:w2-3] + "..."
        print(f"{n:<{w1}} | {show:<{w2}} | {token_name:<{w3}} | {val:<{w4}}")

def print_summary(rows: List[Tuple[int, str, str, bool]]) -> None:
    """Resumen por tipo."""
    by_type: Dict[str, int] = {}
    total = len(rows)
    validos = sum(1 for _, _, _, ok in rows if ok)
    for _, _, t, _ in rows:
        by_type[t] = by_type.get(t, 0) + 1
    print("\nResumen:")
    print(f"  Total tokens: {total}")
    print(f"  Válidos: {validos}  |  Inválidos: {total - validos}")
    for t, c in sorted(by_type.items(), key=lambda x: (-x[1], x[0])):
        print(f"  {t}: {c}")
# --------------------------------------------------------


# ------------------------- Main -------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Validador de tokens con Expresiones Regulares (INFO1148)."
    )
    parser.add_argument("input", help="Ruta al archivo .txt (líneas o párrafos).")
    args = parser.parse_args()

    patterns = build_patterns()
    rows: List[Tuple[int, str, str, bool]] = []

    try:
        with open(args.input, "r", encoding="utf-8") as f:
            for i, raw in enumerate(f, start=1):
                line = raw.strip()
                if not line:
                    continue
                for tok in tokenize(line):
                    token_name, ok = classify(tok, patterns)
                    rows.append((i, tok, token_name, ok))
    except FileNotFoundError:
        print(f"ERROR: No se encontró el archivo: {args.input}")
        return
    except UnicodeDecodeError:
        print("ERROR: Problema de codificación. Usa UTF-8 en el archivo de entrada.")
        return

    print_table(rows)
    print_summary(rows)

if __name__ == "__main__":
    main()
