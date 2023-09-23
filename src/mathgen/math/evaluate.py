import ast

from .evalfuncs.all import EVALFUNCS
from .precise_num import PN

GIVEN_GLOBALS = {
    "PN": PN,
} | EVALFUNCS

def evaluate_expression(expr_str: str, globals={}, locals={}):
    globals = {**globals, **GIVEN_GLOBALS}
    expr = ast.parse(expr_str, mode="eval")
    expr = ast.fix_missing_locations(rewrite_constants().visit(expr))
    return eval(ast.unparse(expr), globals, locals)

class rewrite_constants(ast.NodeTransformer):
    def visit_Constant(self, node: ast.Constant):
        if isinstance(node.value, int | float):
            return ast.parse(f"PN({node.value})", mode="eval").body
        return node


# poetry run python -m src.mathgen.math.evaluate
if __name__ == "__main__":
    expressions = [
        "23",
        "-42",
        "5 + 8",
        "3 + 5 * 8",
        "range(5)",
        "[x for x in range(5) if x % 2]"
    ]
    for expr in expressions:
        print(expr, "=", evaluate_expression(expr))


