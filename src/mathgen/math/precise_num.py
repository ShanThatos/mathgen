import math
from fractions import Fraction
from functools import wraps
from typing import Literal, Optional

WRAPPED_FUNCS = [
    "add", "sub", "mul", "truediv", "floordiv", "mod", "divmod", "pow",
    "pos", "neg", "abs", "int", "ceil", "floor", "round", "trunc",
    "eq", "ne", "lt", "le", "gt", "ge",
    "copy", "deepcopy",
    "bool", "hash"
]


def add_fraction_methods(cls):
    def make_wrapper(func_name):
        @wraps(getattr(Fraction, func_name))
        def func(self, *args, **kwargs):
            args = [arg._frac if isinstance(arg, PN) else arg for arg in args]
            result = getattr(self._frac, func_name)(*args, **kwargs)
            if isinstance(result, Fraction):
                return cls(result.numerator, result.denominator)
            return result
        return func
    for func_name in WRAPPED_FUNCS:
        func_name = f"__{func_name}__"
        setattr(cls, func_name, make_wrapper(func_name))
    return cls


# Precise Number
@add_fraction_methods
class PN:
    def __init__(self, num: int = 0, den: int = 1):
        self._frac = Fraction(num, den)

    @property
    def num(self):
        return self._frac.numerator
    
    @property
    def den(self):
        return self._frac.denominator
    
    @property
    def is_integer(self):
        return self.den == 1
    
    @property
    def is_fraction(self):
        return not self.is_integer

    @property
    def is_proper(self):
        return self.is_fraction and abs(self.num) < self.den
    
    @property
    def is_improper(self):
        return self.is_fraction and not self.is_proper
    

    def __format__(self, format_spec: str):
        if format_spec.startswith("latex"):
            latex_format = None
            if ":" in format_spec:
                latex_format = format_spec.split(":", 1)[1]
            return self.as_latex(format=latex_format)
        return self._frac.__format__(format_spec)
    
    # format: Optional[Literal["integer", "fraction", "mixed", "decimal", "all"]]
    def as_latex(self, format = None):
        if format is None:
            format = "integer" if self.is_integer else "mixed" if self.is_improper else "fraction"
        sign = "-" if self.num < 0 else ""
        num, den = abs(self.num), self.den
        outputs = []
        if self.is_integer and format in ("integer", "all"):
            outputs.append(f"{sign}{num}")
        if self.is_fraction and format in ("fraction", "all"):
            outputs.append(f"{sign}\\frac{{{num}}}{{{den}}}")
        if self.is_improper and format in ("mixed", "all"):
            outputs.append(f"{sign}{num // den or ""}\\frac{{{num % den}}}{{{den}}}")

        if not outputs:
            raise ValueError(f"invalid format {repr(format)} for {repr(self)}")
        
        distinct_outputs = []
        for output in outputs:
            if output not in distinct_outputs:
                distinct_outputs.append(output)

        return ",".join(distinct_outputs)


    def __str__(self):
        return str(self._frac)
    
    def __repr__(self):
        if self.den == 1:
            return f"PN({self.num})"
        return f"PN({self.num}, {self.den})"


# poetry run python -m src.mathgen.math.precise_num
if __name__ == '__main__':
    # print(PN(2))
    # print(PN(2) + PN(5))

    # print(PN(13) / PN(3))
    # print(PN(13) // PN(3))
    
    # print(eval(repr(PN(5, 3))))
    pass