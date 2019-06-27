"""
__init__.py

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""

from . import administration
from . import board

# yes this code is technically unreachable, this is by design.
# noinspection PyUnreachableCode
if __debug__:
    from . import debug

__all__ = ["administration", "board"]
