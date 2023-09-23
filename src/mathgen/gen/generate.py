from ..math.evaluate import evaluate_expression
from .mathproblem import MathProblem, MathProblemModel, split_prefix


class MathProblemGenerator:
    MAX_TRIES = 50

    def __init__(self, model: MathProblemModel):
        self.model = model

    def generate(self) -> MathProblem:
        for _ in range(self.MAX_TRIES):
            problem = MathProblem(model=self.model)
            for line in self.model.gen:
                prefix_line = split_prefix(line)
                assert(prefix_line is not None)
                prefix, line = prefix_line
                getattr(self, f"_gen_{prefix}")(problem, line)
                if not problem.valid:
                    break
            else:
                return problem
        raise RuntimeError(f"failed to generate a valid problem for {self.model.name}")
    
    def _gen_var(self, problem: MathProblem, line: str):
        name, expr = line.split("=", 1)
        problem.vars[name.strip()] = evaluate_expression(expr.strip(), locals=problem.vars)

    def _gen_condition(self, problem: MathProblem, line: str):
        problem.valid &= evaluate_expression(line.strip(), locals=problem.vars)

    def _gen_problem(self, problem: MathProblem, line: str):
        problem.question = eval("f\"$" + repr(line.strip())[1:-1] + "$\"", {}, problem.vars)

    def _gen_answer(self, problem: MathProblem, line: str):
        problem.answer = eval("f\"$" + repr(line.strip())[1:-1] + "$\"", {}, problem.vars)


if __name__ == "__main__":
    model = MathProblemModel(
        id="1",
        name="test",
        gen=[
            "@var a = rand(3, 100) / rand(3, 10)",
            "@var b = rand(3, 100) / rand(3, 10)",
            "@condition btwn(a, 1, 10) and btwn(b, 1, 10) and is_improper(a, b)",
            "@problem {a:latex:mixed} \\times {b:latex:mixed}?",
            "@answer {a * b:latex}"
        ],
    )

    generator = MathProblemGenerator(model)
    problem = generator.generate()
    print(problem.vars)
    print(problem.question)
    print(problem.answer)