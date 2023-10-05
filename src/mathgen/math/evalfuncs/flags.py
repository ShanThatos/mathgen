# type: ignore

from ..precise_num import PN
from .capture import use_as_global


@use_as_global("is_integer")
def _is_integer(*args: PN):
    return all(x.is_integer for x in args)

@use_as_global("is_fraction")
def _is_fraction(*args: PN):
    return all(x.is_fraction for x in args)

@use_as_global("is_proper")
def _is_proper(*args: PN):
    return all(x.is_proper for x in args)

@use_as_global("is_improper")
def _is_improper(*args: PN):
    return all(x.is_improper for x in args)
