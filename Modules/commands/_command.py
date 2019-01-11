"""
_command.py - {summery}

{long description}

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
from asyncio import run
from collections import abc
from contextlib import suppress
from logging import getLogger
from typing import List, Callable

from Modules.commands._hooks import CancelExecution
from Modules.context import Context
from . import _hooks

LOG = getLogger(f"mecha.{__name__}")

ENABLED = object()


class Command(abc.Container):
    """
    Defines a Command.

    Examples:
        This class implements :class:`abc.Container`, using string aliases for the contains check.
        >>> async def foo(*args, **kwargs):
        ...     print("foo called!")
        >>> cmd = Command('doc_command_foo', underlying=foo)

        >>> 'doc_command_foo' in cmd
        True

        Instances of this class are callable,
        >>> run(cmd(None))
        foo called!
    """
    __slots__ = [
        '_underlying',
        'hooks',
        '_aliases'
    ]

    def __init__(self, *names,
                 underlying: Callable,
                 **kwargs):

        if not names:
            raise ValueError("at least one name is required.")

        if 'require_dm' in kwargs and 'require_channel' in kwargs:
            raise ValueError("require_dm and require_channel are mutually exclusive.")

        self.hooks: List = []  # todo proper type hint

        self._aliases: List[str] = names

        self._underlying = underlying

        # for each kwarg
        for key, value in kwargs.items():
            # match it to its corresponding hook

            if value is not ENABLED:
                # if the value is not Enabled, pass the value to the hook's constructor
                hook = _hooks.hooks[key](value)
            else:
                hook = _hooks.hooks[key]()  # otehrwise allow the default to be used instead
            self.hooks.append(hook)

    def __contains__(self, item: str):
        # check if its a string
        if not isinstance(item, str):
            # its not, bailout
            return NotImplemented
        # check if the specified item is one of ours
        return item in self.aliases

    @property
    def name(self):
        """
        return the first alias this command is known by, aka its name
        """
        return self.aliases[0]

    @property
    def underlying(self) -> Callable:
        """
        The underlying command function, with no setup_hooks applied.
        """
        return self._underlying

    @property
    def aliases(self) -> List[str]:
        """
        Lists of alias the underlying can be invoked by
        """
        return self._aliases

    async def __call__(self, context: Context):
        """
        Invoke this command.

        First thing this function does is call the setup hooks, allowing for pre-command execution
        behavior.
        If any of the setup hooks return :obj:`_hooks.STOP_EXECUTION` then execution will be
        canceled.

        Any uncalled setup hooks are discarded, and the underlying / teardown hooks are
        also discarded.

        Args:
            *args: Positional arguments to pass to hooks and underlying
            **kwargs (): Keyword arguments to pass to hooks and underlying
        """

        LOG.debug(f"command {self.aliases[0]} invoked...")

        # initialize each generator
        hook_gens = (hook(context) for hook in self.hooks)

        executed_gens = set()

        extra_arguments = {}

        try:
            for hook in hook_gens:
                LOG.debug(f"calling setup for hook {hook}...")
                result = await next(hook)

                # keep track of which generators we have actually executed for teardown

                executed_gens.add(hook)
                if result:
                    extra_arguments.update(result)
        except CancelExecution:
            LOG.debug("setup task canceled event execution.")

        else:
            LOG.debug(f"calling underlying with extra_args:= {extra_arguments}")
            await self.underlying(context=context, **extra_arguments)

        finally:
            for hook in executed_gens:
                with suppress(StopIteration):
                    await next(hook)
