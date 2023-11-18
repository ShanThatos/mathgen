# type: ignore

import math

from ..precise_num import PN
from .capture import use_as_global


@use_as_global("is_prime")
def _is_prime(*args: PN):
    for x in args:
        if not x.is_integer:
            return False
        if abs(x.num) == 2:
            return True
        for i in range(3, abs(x.num), 2):
            if x.num % i == 0:
                return False
    return True


@use_as_global("gcd")
def _gcd(*args: PN):
    if len(args) == 1:
        return args[0]
    if len(args) == 2:
        a, b = args
        return PN(math.gcd(a.num, b.num), math.lcm(a.den, b.den))
    return _gcd(args[0], _gcd(*args[1:]))


@use_as_global("lcm")
def _lcm(*args: PN):
    if len(args) == 1:
        return args[0]
    if len(args) == 2:
        a, b = args
        return PN(math.lcm(a.num, b.num), math.gcd(a.den, b.den))
    return _lcm(args[0], _lcm(*args[1:]))
