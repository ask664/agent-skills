---
name: calculator
description: Perform addition, subtraction, multiplication, or division of two decimal numbers when the user needs an exact arithmetic result.
compatibility: Requires Python 3 and a runtime tool that can execute bundled scripts.
metadata:
  version: "1.0.0"
---

# Calculator

Run `python3 scripts/calculate.py OPERATION A B` from this skill's directory.
Operations are `add`, `subtract`, `multiply`, and `divide`. Pass numeric operands
as separate arguments; do not generate or evaluate code from the expression.
Read [the input contract](references/input.schema.json) when mapping arguments.
Report the JSON `result`. On invalid input or division by zero, report the error
and request corrected operands. Decimal results use 28 significant digits.

Example: `python3 scripts/calculate.py multiply 12.5 8` returns `{"result": "100.0"}`.
If execution is unavailable, explain that this skill needs a script execution tool.
