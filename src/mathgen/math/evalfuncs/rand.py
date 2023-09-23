import math
import random

from ..precise_num import PN
from .capture import start_stop_step_args, use_as_global


@use_as_global("rand")
def _rand(*args):
    start, stop, step = start_stop_step_args(args)
    return PN(random.randrange(math.floor(start), math.floor(stop), math.floor(step))) # type: ignore

