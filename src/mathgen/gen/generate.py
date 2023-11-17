import random
import re
import threading
from typing import Dict, List

from ..math.evaluate import evaluate_expression
from .mathproblem import (
    MathGenCode,
    MathProblem,
    MathProblemFormat,
    MathProblemModel,
    split_prefix,
)

ANSWER_FORMATS: Dict[MathProblemFormat, re.Pattern] = {
    "number": re.compile(r"^\$-?\d+\$$"),
    "decimal": re.compile(r"^\$-?\d+\.\d+\$$"),
    "fraction": re.compile(r"^\$-?\\frac{\d+}{\d+}\$$"),
    "mixed": re.compile(r"^\$-?\d+\\frac{\d+}{\d+}\$$")
}

def recognize_answer_format(answer: str) -> MathProblemFormat:
    for format, regex in ANSWER_FORMATS.items():
        if regex.match(answer):
            return format
    raise ValueError(f"Didn't find matching answer format for: {repr(answer)}")

QA_GLOBALS = {
    "blank": r"\underline{\quad}"
}

class MathProblemGenerator:
    MAX_TRIES = 50

    def __init__(self, model: MathProblemModel, seed=None):
        self.model = model
        self.seed = seed
        self.__current_seed = seed
        self.__generate_lock = threading.Lock()

    def _generate(self) -> MathProblem:
        for _ in range(self.MAX_TRIES):
            self.vars = {}
            self.questions = set()
            self.problem = MathProblem(id=self.model.id, format=self.model.format, units=self.model.units, rtl=self.model.rtl)
            for line in self.model.code.splitlines():
                line = line.strip()
                if not line:
                    continue
                prefix_line = split_prefix(line)
                assert prefix_line is not None
                prefix, line = prefix_line
                if getattr(self, f"_gen_{prefix}")(line) == False:
                    break
                self._step_current_seed()
            else:
                if self.questions:
                    self.problem.question = random.Random(self.__current_seed).choice(list(self.questions))
                return self.problem
        raise RuntimeError(f"Failed to generate a valid problem for {self.model.id}")

    def generate(self) -> MathProblem:
        with self.__generate_lock:
            self.__current_seed = self.seed
            problem = self._generate()
            self.__current_seed = self.seed
        return problem

    def generate_multiple(self, n: int) -> List[MathProblem]:
        with self.__generate_lock:
            self.__current_seed = self.seed
            self.vars_list = []
            problems: List[MathProblem] = []
            failures = 0
            while len(problems) < n:
                problem = self._generate()
                self._step_current_seed()
                if failures < 10:
                    if self.vars in self.vars_list:
                        failures += 1
                        continue
                    if any(problem.question == p.question and problem.answer == p.answer for p in problems):
                        failures += 1
                        continue
                failures = 0
                
                problems.append(problem)
                self.vars_list.append(self.vars.copy())
            self.__current_seed = self.seed
        return problems

    def _gen_var(self, line: str):
        name, expr = line.split("=", 1)
        self.vars[name.strip()] = evaluate_expression(
            expr.strip(), locals=self.vars, seed=self.__current_seed
        )

    def _gen_condition(self, line: str):
        return evaluate_expression(
            line.strip(), locals=self.vars, seed=self.__current_seed
        )

    def _gen_question(self, line: str):
        self.questions.add(eval(f"f{repr("$" + line.strip() + "$")}", QA_GLOBALS, self.vars))

    def _gen_answer(self, line: str):
        self.problem.answer = eval(f"f{repr("$" + line.strip() + "$")}", QA_GLOBALS, self.vars)
        if self.problem.format == "auto":
            self.problem.format = recognize_answer_format(self.problem.answer)

    def _gen_group(self, line: str):
        raise Exception("Group directive not handled by mathgen core")

    def _step_current_seed(self):
        if isinstance(self.__current_seed, int):
            self.__current_seed = (
                self.__current_seed**2 * 3041 + self.__current_seed * 1009
            ) % 1000000007


# poetry run python -m src.mathgen.gen.generate
if __name__ == "__main__":
    model = MathProblemModel(
        id="test",
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

    generator = MathProblemGenerator(model, seed=20)
    problem = generator.generate()
    print(problem.question)
    print(problem.answer)

    print(problem.model_dump_json())

    # print(generator.generate_multiple(5))
