from typing import TypeVar, Generic, List
from uuid import UUID

from Modules.rat import Rat as _Rat
from Modules.rat_rescue import Rescue as _Rescue

# typedefs to builtin types (OK For export)
Index = int
Name = str
Word = str
# typeVars (OK for export)
Remainder = TypeVar("Remainder", bound=List[str])
"""
Any remaining unprocessed words, this argument should come last
"""

# typeVars (Not for Export)
_RescueType = TypeVar("_RescueType", _Rescue, Index, Name, UUID)  # Rescue type
_RatType = TypeVar("_RatType", Name, UUID, _Rat)  # rat type


# generic types (OK for export)

class Rescue(Generic[_RescueType], _Rescue):
    """
    Rescue type parameter, for use with `@parametrize`

    Functions using this hint will have an argument block added to it to find a Rescue from the
    context by the parametrize decorator

    Basic usage:
        >>> def foo(rescue:Rescue):
        ...     ...

    Parametrize will create a positional argument group for the argument.
    This group accepts a String commander name, a integer case index, or a UUID

    If it is desirable to restrict /how/ this argument is parametrized, a type can be specified.

    For instance, if we want it to only find Rescues by a specified Commander Name,
        >>> def foo(rescue:Rescue[Name]):
        ...     ...


    Rescues can also be parametrized by their index:
        >>> def foo(rescue:Rescue[Index]):
        ...     ...

        Parametrize will register a positional integer argument for `rescue_a` that will resolve
        to a Rescue on the Context.bot.board object by its index.


    Alternatively, they can be parametrized by their api ID:
        >>> def foo(rescue:Rescue[UUID]):
        ...     ...

    Please note that the optional filtering types are mutually exclusive, and cannot be mixed.
    """
    ...


class Rat(Generic[_RatType], _Rat):
    """
    Rat type parameter, for use with `@parametrize`

    arguments with this type hint will have a Rat argument block added to their CLI invocations.

    Usage:
        Define a command that accepts a rat object by any method
            >>> def foo(rat:Rat):
            ...     ...

        Define a command that accepts a rat only by UUID
            >>> def foo(rat:Rat[UUID]):
            ...     ...

        Define a command that accepts a rat only by Name:
            >>> def foo(rat:Rat[Name]):
            ...     ...

    """
    ...
