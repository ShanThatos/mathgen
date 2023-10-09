from typing import Annotated, Any, Dict, Optional, Tuple

from pydantic import AfterValidator, BaseModel, PlainSerializer, TypeAdapter

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


class MathProblemModel(BaseModel):
    id: int
    name: str
    code: MathGenCode


MathProblemModelAdapter = TypeAdapter(MathProblemModel)

SerializableVar = Annotated[
    Any,
    PlainSerializer(lambda x: repr(x), return_type=str),
]


class MathProblem(BaseModel):
    name: str = ""
    question: str = ""
    answer: str = ""
    vars: Dict[str, SerializableVar] = {}
