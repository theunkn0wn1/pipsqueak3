from typing import TypeVar, Generic, TYPE_CHECKING, Union
from uuid import UUID

from Modules.rat_rescue import Rescue as _Rescue

from Modules.rat import Rat as _Rat
if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from utils.ratlib import Platforms as _Platforms


# typedefs to builtin types (OK For export)
Index = int
Name = str

# typeVars (OK For Export)
RescueType = TypeVar('RescueType', int, Name, UUID)  # Rescue type
RatType = TypeVar("RatType", '_Platforms', str, UUID)  # rat type


class Rescue(Generic[RescueType], _Rescue):
    """
    Rescue type parameter, for use with @parametrize

    Functions using this hint will have an argument block added to it to find a Rescue from the
    context by the parametrize decorator

    Basic usage:
        >>> def foo(rescue:Rescue):
        ...     ...

    Parametrize will create a positional argument group for the argument.
    This group accepts a String commander name, a integer case index, or a UUID

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


class Rat(Generic[RatType], _Rat):
    ...
