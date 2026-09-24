import argparse
import json
from decimal import Decimal, DecimalException


def calculate(operation, a, b):
    a, b = Decimal(a), Decimal(b)
    if not a.is_finite() or not b.is_finite():
        raise ValueError("Operands must be finite")
    operations = {
        "add": lambda: a + b,
        "subtract": lambda: a - b,
        "multiply": lambda: a * b,
        "divide": lambda: a / b,
    }
    return str(operations[operation]())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("operation", choices=["add", "subtract", "multiply", "divide"])
    parser.add_argument("a")
    parser.add_argument("b")
    args = parser.parse_args()
    try:
        print(json.dumps({"result": calculate(args.operation, args.a, args.b)}))
    except (ValueError, DecimalException) as error:
        print(json.dumps({"error": str(error)}))
        raise SystemExit(1)
