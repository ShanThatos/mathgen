from fractions import Fraction
from functools import wraps
from typing import Literal, Optional

WRAPPED_FUNCS = [
    "add",
    "sub",
    "mul",
    "truediv",
    "floordiv",
    "mod",
    "divmod",
    "pow",
    "pos",
    "neg",
    "abs",
    "int",
    "ceil",
    "floor",
    "round",
    "trunc",
    "eq",
    "ne",
    "lt",
    "le",
    "gt",
    "ge",
    "copy",
    "deepcopy",
    "bool",
    "hash",
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

    @property
    def is_repeating(self):
        num, den = abs(self.num), self.den
        num %= den
        digits = set()
        while num:
            if num in digits:
                return True
            digits.add(num)
            num = num * 10 % den
        return False

    def __format__(self, spec: str):
        options = None
        if ":" in spec:
            spec, options = spec.split(":", 1)
        return self.as_latex(format=spec, options=options)  # type: ignore

    def as_latex(
        self,
        format: Optional[
            Literal["integer", "fraction", "mixed", "decimal", "all"]
        ] = None,
        options: Optional[str] = None,
    ):
        if not format:
            format = (
                "integer"
                if self.is_integer
                else "mixed"
                if self.is_improper
                else "fraction"
            )
        sign = "-" if self.num < 0 else ""
        num, den = abs(self.num), self.den
        outputs = []
        if self.is_integer and format in ("integer", "all"):
            outputs.append(f"{sign}{num}")
        if self.is_fraction and format in ("fraction", "all"):
            outputs.append(rf"{sign}\frac{{{num}}}{{{den}}}")
        if self.is_improper and format in ("mixed", "all"):
            outputs.append(rf"{sign}{num // den or " "}\frac{{{num % den}}}{{{den}}}")

        if format == "decimal":
            num_decimals = 3
            options = options or ""
            digits = "".join(ch for ch in options if ch.isdigit())
            if digits:
                num_decimals = int(digits)
            outputs.append(self.as_decimal(num_decimals=num_decimals))

        if not outputs:
            raise ValueError(f"invalid format {repr(format)} for {repr(self)}")

        distinct_outputs = []
        for output in outputs:
            if output not in distinct_outputs:
                distinct_outputs.append(output)

        return ",".join(distinct_outputs)

    def as_decimal(self, num_decimals: int = 3):
        if num_decimals < 0:
            raise ValueError(f"invalid number of decimals {num_decimals}")

        if self.num == 0:
            return "0"

        sign = "-" if self.num < 0 else ""
        num, den = abs(self.num), self.den

        if num_decimals == 0:
            result = num // den + (num % den * 2 >= den)
            if result == 0:
                return "0"
            return sign + str(result)

        digits = []
        if num // den:
            digits.extend(int(ch) for ch in str(num // den))
            num %= den

        decimal_index = len(digits)
        for _ in range(num_decimals):
            num *= 10
            digits.append(num // den)
            num %= den

        if num * 2 >= den:
            carry = 1
            i = len(digits) - 1
            while carry:
                if i < 0:
                    digits.insert(0, 0)
                    decimal_index += 1
                    i = 0
                digits[i] += carry
                carry = digits[i] // 10
                digits[i] %= 10
                i -= 1

        digits.insert(decimal_index, ".")
        digits.insert(0, sign)
        while digits[-1] == 0:
            digits.pop()
        if digits[-1] == ".":
            digits.pop()
        return "".join(str(digit) for digit in digits)

    def __str__(self):
        return self.as_latex()

    def __repr__(self):
        if self.den == 1:
            return f"PN({self.num})"
        return f"PN({self.num}, {self.den})"


# poetry run python -m src.mathgen.math.precise_num
if __name__ == "__main__":
    # print(PN(2))
    # print(PN(2) + PN(5))

    # print(PN(13) / PN(3))
    # print(PN(13) // PN(3))

    # print(eval(repr(PN(5, 3))))

    # print((PN(-15) / PN(10)).as_decimal(5))
    pass
