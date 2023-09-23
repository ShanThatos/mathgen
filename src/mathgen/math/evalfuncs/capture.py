# type: ignore

from ..precise_num import PN

GLOBALS = {}
def use_as_global(name=None):
    def decorator(func):
        GLOBALS[name or func.__name__] = func
        return func
    return decorator

def start_stop_step_args(args):
    start = PN(0)
    stop = PN(0)
    step = PN(1)
    if len(args) == 1:
        stop = args[0]
    elif len(args) == 2:
        start, stop = args
    elif len(args) == 3:
        start, stop, step = args
    else:
        raise TypeError(f"expected at most 3 arguments, got {len(args)}")
    return start, stop, step # type: ignore
