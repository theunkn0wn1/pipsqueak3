"""
method_dispatch.py - Singledispatch for instance methods

{long description}

Content originally from StackOverflow

Attribution information
-------------------------

Original Question: https://stackoverflow.com/questions/24601722/how-can-i-use-functools-singledispatch-with-instance-methods
Source: https://stackoverflow.com/a/24602374
Author: zero-piraeus https://stackoverflow.com/users/1014938/zero-piraeus


COPYRIGHT
-------------------------
    Licensed under cc by-sa 3.0 with attribution required.

Modifications Made
--------------------------
    renamed function to match project style requirements
"""

from functools import singledispatch, update_wrapper


def method_dispatch(func):
    """
    functools.singledispatch for instance methods
    Args:
        func (): instance method
    """
    dispatcher = singledispatch(func)

    def wrapper(*args, **kw):
        return dispatcher.dispatch(args[1].__class__)(*args, **kw)

    wrapper.register = dispatcher.register
    update_wrapper(wrapper, func)
    return wrapper
