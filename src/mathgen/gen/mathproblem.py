from typing import Annotated, Any, Dict, List, Optional, Tuple

from pydantic import AfterValidator, BaseModel, TypeAdapter

PREFIXES = ["var", "condition", "question", "answer"]


def split_prefix(line: str) -> Optional[Tuple[str, str]]:
    line = line.strip()
    for prefix in PREFIXES:
        if line.startswith(f"@{prefix} "):
            return prefix, line[len(prefix) + 2 :].strip()
    return None


def mathgen_line_validator(line: str) -> str:
    if split_prefix(line) is None:
        raise ValueError(f"invalid line, must start with one of {PREFIXES}")
    return line


MathGenLine = Annotated[str, AfterValidator(mathgen_line_validator)]


class MathProblemModel(BaseModel):
    id: int
    name: str
    gen: List[MathGenLine]


MathProblemModelAdapter = TypeAdapter(MathProblemModel)


class MathProblem(BaseModel):
    model_name: str
    question: str = ""
    answer: str = ""
    valid: bool = True
    vars: Dict[str, Any] = {}


if __name__ == "__main__":
    problem = MathProblemModel(
        id=1,
        name="test",
        gen=[
            "@var a = 1",
            "@var b = 2",
            "@condition a < b",
            "@question a + b = ?",
            "@answer 3",
        ],
    )
    print(problem)

    print(MathProblemModelAdapter.dump_json(problem))
