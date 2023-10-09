import threading
from typing import List

from ..math.evaluate import evaluate_expression
from .mathproblem import MathProblem, MathProblemModel, split_prefix


class MathProblemGenerator:
    MAX_TRIES = 50

    def __init__(self, name: str, code: str, seed=None):
        self.name = name
        self.code = code
        self.seed = seed
        self.__current_seed = seed
        self.__current_seed_lock = threading.Lock()

    def generate(self) -> MathProblem:
        for _ in range(self.MAX_TRIES):
            problem = MathProblem(name=self.name)
            for line in self.code.splitlines():
                line = line.strip()
                if not line:
                    continue
                prefix_line = split_prefix(line)
                assert prefix_line is not None
                prefix, line = prefix_line
                if getattr(self, f"_gen_{prefix}")(problem, line) == False:
                    break
            else:
                return problem
        raise RuntimeError(f"Failed to generate a valid problem for {self.name}")

    def generate_multiple(self, n: int) -> List[MathProblem]:
        with self.__current_seed_lock:
            self.__current_seed = self.seed
            problems: List[MathProblem] = []
            for _ in range(n):
                problems.append(self.generate())
                if isinstance(self.__current_seed, int):
                    self.__current_seed = (
                        self.__current_seed**2 * 3041 + self.__current_seed * 1009 + 1
                    )
            self.__current_seed = self.seed
        return problems

    def _gen_var(self, problem: MathProblem, line: str):
        name, expr = line.split("=", 1)
        problem.vars[name.strip()] = evaluate_expression(
            expr.strip(), locals=problem.vars, seed=self.__current_seed
        )

    def _gen_condition(self, problem: MathProblem, line: str):
        return evaluate_expression(
            line.strip(), locals=problem.vars, seed=self.__current_seed
        )

    def _gen_question(self, problem: MathProblem, line: str):
        problem.question = eval(f"f{repr(line.strip())}", {}, problem.vars)

    def _gen_answer(self, problem: MathProblem, line: str):
        problem.answer = eval(f"f{repr(line.strip())}", {}, problem.vars)

    @classmethod
    def from_model(cls, model: MathProblemModel, *args, **kwargs):
        return cls(model.name, model.code, *args, **kwargs)


# poetry run python -m src.mathgen.gen.generate
if __name__ == "__main__":
    model = MathProblemModel(
        id=1,
        name="test",
        code="\n".join(
            [
                "@var a = rand(3, 100) / rand(3, 10)",
                "@var b = rand(3, 100) / rand(3, 10)",
                "@condition a < 10 and b < 10 and is_improper(a, b)",
                "@question {a} \\times {b}?",
                "@answer {a * b}",
            ]
        ),
    )

    generator = MathProblemGenerator.from_model(model)
    problem = generator.generate()
    print(problem.vars)
    print(problem.question)
    print(problem.answer)

    print(problem.model_dump_json())
