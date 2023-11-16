from typing import Annotated, Any, Dict, Literal, Optional, Tuple

from pydantic import AfterValidator, BaseModel, Field, PlainSerializer, TypeAdapter

PREFIXES = ["var", "condition", "question", "answer"]


def split_prefix(line: str) -> Optional[Tuple[str, str]]:
    line = line.strip()
    for prefix in PREFIXES:
        if line.startswith(f"@{prefix} "):
            return prefix, line[len(prefix) + 2 :].strip()
    return None


def mathgen_validator(code: str) -> str:
    lines = (x for x in code.splitlines() if x.strip())
    for line in lines:
        if split_prefix(line) is None:
            raise ValueError(f"invalid line, must start with one of {PREFIXES}")
    return code


MathGenCode = Annotated[str, AfterValidator(mathgen_validator)]

type MathProblemFormat = Literal[
    "auto", "number", "decimal", "money", "fraction", "mixed"
]


class MathProblemModel(BaseModel):
    id: str
    format: MathProblemFormat = "auto"
    code: MathGenCode


MathProblemModelAdapter = TypeAdapter(MathProblemModel)


class MathProblem(BaseModel):
    id: str
    format: MathProblemFormat = "auto"
    question: str = ""
    answer: str = ""
