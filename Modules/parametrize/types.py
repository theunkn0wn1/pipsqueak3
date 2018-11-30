from typing import TypeVar, Generic

from Modules.rat_rescue import Rescue as _Rescue

RT = TypeVar('RT', _Rescue, int, str)  # Rescue type


class Rescue(Generic[RT]):
    def __repr__(self):
        return "types.Rescue"


def foo(bar: Rescue[str]):
    print(bar)


mdata = _Rescue(None, None, None, None)


def bar() -> Rescue[int]:
    ...


foo(bar())
