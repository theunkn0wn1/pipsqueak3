"""
rat_rescue.py - Rescue board and objects

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.
"""
from __future__ import annotations
import logging
import typing
from contextlib import contextmanager
from datetime import datetime
from uuid import UUID, uuid4

from ..cache import RatCache
from ..epic import Epic
from ..mark_for_deletion import MarkForDeletion
from ..quotation import Quotation
from ..rat import Rat
from ..utils import Platforms, Status

LOG = logging.getLogger(f"mecha.{__name__}")


class Rescue:  # pylint: disable=too-many-public-methods
    """
    A unique rescuer
    """
    __slots__ = ["_platform",
                 "_rats",
                 "_created_at",
                 "_updated_at",
                 "_api_id",
                 "_client",
                 "_irc_nick",
                 "_unidentified_rats",
                 "_system",
                 "_active",
                 "_quotes",
                 "_epic",
                 "_code_red",
                 "_outcome",
                 "_title",
                 "_first_limpet",
                 "_board_index",
                 "_mark_for_deletion",
                 "_board_index",
                 "_lang_id",
                 "_status",
                 "_hash",
                 "_modified_attrs"]

    def __init__(self,  # pylint: disable=too-many-locals
                 uuid: UUID = None,
                 client: typing.Optional[str] = None,
                 system: typing.Optional[str] = None,
                 irc_nickname: typing.Optional[str] = None,
                 unidentified_rats: typing.Optional[typing.List[str]] = None,
                 active: bool = True,
                 quotes: typing.Optional[typing.List[Quotation]] = None,
                 epic: typing.List[Epic] = None,
                 title: typing.Optional[str] = None,
                 first_limpet: typing.Optional[UUID] = None,
                 board_index: typing.Optional[int] = None,
                 mark_for_deletion: MarkForDeletion = MarkForDeletion(),
                 lang_id: str = "EN",
                 rats: typing.List[Rat] = None,
                 status: Status = Status.OPEN,
                 code_red=False,
                 platform: Platforms = None):
        """
        creates a rescue

        Args:
            code_red (bool): is the client on emergency oxygen
            status (Status): status attribute for the rescue
            board (RatBoard): RatBoard instance this rescue is attached to, if any.
            uuid (str): API id of rescue
            client (str): Commander name of the Commander rescued
            system (str): System name the Commander is stranded in
                (WILL BE CAST TO UPPER CASE)
            unidentified_rats (list): list of unidentified rats responding to
                rescue **(nicknames)**
            active (bool): marks whether the case is active or not
            quotes (list): list of Quotation objects associated with rescue
            epic (bool): is the case marked as an epic
            title (str): name of operation, if applicable
            first_limpet (UUID): Id of the rat that got the first limpet
            board_index (int): index position on the board, if any.
            mark_for_deletion (dict): the markForDeletion object for the API,
                if any.
                - will default to open and not MD'ed
            lang_id (str): language ID of the client, defaults to english.
            irc_nickname (str): clients IRC nickname, may deffer from their
                commander name.
            rats (list): identified Rat(s) assigned to rescue.
            platform(Platforms): Platform for rescue
        """
        self._modified_attrs: typing.Set[str] = set()
        self._platform: Platforms = platform
        self._rats = rats if rats else []
        self._api_id: UUID = uuid if uuid else uuid4()
        self._client: str = client
        self._irc_nick: str = irc_nickname
        self._unidentified_rats = unidentified_rats if unidentified_rats else []
        self._system: str = system.upper() if system else None
        self._active: bool = active
        self._quotes: list = quotes if quotes else []
        self._epic: typing.List[Epic] = epic if epic is not None else []
        self._code_red: bool = code_red
        self._outcome: None = None
        self._title: typing.Optional[str] = title
        self._first_limpet: UUID = first_limpet
        self._board_index = board_index
        self._mark_for_deletion = mark_for_deletion
        self._board_index = board_index
        self._lang_id = lang_id
        self._status = status
        self._hash = None

    def __eq__(self, other) -> bool:
        """
        Verify `other` is equal to the self.

        Args:
            other (Rescue): Rescue to compare against

        Returns:
            bool: is equivalent
        """
        if not isinstance(other, Rescue):
            # instance type check
            return NotImplemented
        return other.api_id == self.api_id

    def __hash__(self):

        if self._hash is None:
            self._hash = hash(self.api_id)
        return self._hash

    @property
    def status(self) -> Status:
        """
        Status enum for the rescue

        Returns:
            Status
        """
        return self._status

    @status.setter
    def status(self, value: Status):
        """
        Set the value of the status enum

        Args:
            value (Status): new status enum

        Raises:
            TypeError: invalid `value` type
        """
        if isinstance(value, Status):
            self._status = value
            self._modified_attrs.add("status")
        else:
            raise TypeError

    @property
    def irc_nickname(self) -> str:
        """
        The client's irc nickname

        Returns:
            str : nickname
        """
        return self._irc_nick

    @irc_nickname.setter
    def irc_nickname(self, value: str) -> None:
        """
        Sets the client's irc nickname

        Args:
            value (str): new nickname

        Raises:
             TypeError : value was not a string.
        """
        if isinstance(value, str):
            self._irc_nick = value
            self._modified_attrs.add("irc_nickname")
        else:
            raise TypeError

    @property
    def lang_id(self) -> str:
        """
        The language ID the client reported upon entering
        Returns:
            str: clients language ID
        """
        return self._lang_id

    @lang_id.setter
    def lang_id(self, value) -> None:
        """
        Sets the client's language

        Args:
            value (str): new lagnuage code
        """
        if isinstance(value, str):
            self._lang_id = value
            self._modified_attrs.add("lang_id")
        else:
            raise TypeError

    @property
    def platform(self):
        """The Rescue's platform"""
        return self._platform

    @platform.setter
    def platform(self, value) -> None:
        """
        Set the client's platform

        Args:
            value (Platforms): new platform
        """
        if isinstance(value, Platforms):
            self._platform = value
            self._modified_attrs.add("platform")
        else:
            raise TypeError(f"expected a Platforms, got type {type(value)}")

    @property
    def first_limpet(self) -> UUID:
        """
        The ratID of the rat that got the first limpet

        Returns:
            str : ratid
        """
        return self._first_limpet

    @first_limpet.setter
    def first_limpet(self, value: typing.Union[str, UUID]) -> None:
        """
        Set the value of the first limpet rat

        If the value is not a UUID, this method will attempt to coerce it into one.

        Args:
            value (UUID or str): rat id of the first-limpet rat.

        Returns:
            None

        Raises:
            ValueError: The value was not a UUID and could not be parsed into a valid one.
        """
        if isinstance(value, UUID):
            self._first_limpet = value
            self._modified_attrs.add("first_limpet")
        else:
            # the value wasn't a uuid, but lets try and coerce it into one.
            try:
                # try parse
                guid = UUID(value)
            except (ValueError, AttributeError):
                # the attempt failed
                raise TypeError(f"expected UUID, got type {type(value)}")
            else:
                # the attempt succeeded, lets assign it.
                self._first_limpet = guid

    @property
    def board_index(self) -> typing.Optional[int]:
        """
        The position on the rescue board this rescue holds, if any.

        Returns:
            int: if the board is attached to a case, otherwise None
        """
        return self._board_index

    @board_index.setter
    def board_index(self, value: typing.Optional[int]) -> None:
        """
        Sets the Rescue's board index

        Set to None if the rescue is not attached to the board.

        Args:
            value (typing.Optional[int]): index position

        Returns:
            None
        """
        # negative board indexes should not be possible, right?
        if isinstance(value, int) or value is None:
            if value is None or value >= 0:
                self._board_index = value
                self._modified_attrs.add("board_index")
            else:
                raise ValueError("Value must be greater than or equal to zero,"
                                 " or None.")
        else:
            raise TypeError(f"expected int or None, got {type(value)}")

    @property
    def api_id(self) -> UUID:
        """
        The API Id of the rescue.

        Returns: API id

        """

        return self._api_id

    @property
    def client(self) -> str:
        """
        The client associated with the rescue

        Returns:
            (str) the client

        """
        return self._client

    @client.setter
    def client(self, value: str) -> None:
        """
        Sets the client's Commander Name associated with the rescue

        Args:
            value (str): Commander name of the client

        Returns:
            None
        """
        self._client = value
        self._modified_attrs.add("client")

    @property
    def system(self) -> typing.Optional[str]:
        """
        The clients system name

        Returns:
            str: the clients system name
        """
        return self._system

    @system.setter
    def system(self, value: typing.Optional[str]):
        """
        Sets the system property to the upper case of `value`

        Raises:
            AttributeError: if `value` is not a string

        Args:
            value (str): string to set `self.system` to

        Returns:
            None

        Notes:
            this method will cast `value` to upper case, as to comply with
            Fuelrats Api v2.1
        """

        assert value is None or isinstance(value, str)

        if value is None:
            # System must be nullable, so we specifically check for it
            self._system = value
        # for API v2.1 compatibility reasons we cast to upper case
        self._system = value.upper()
        self._modified_attrs.add("system")

    @property
    def active(self) -> bool:
        """
        marker indicating whether a case is active or not. this has no direct
         effect on bot functionality, rather its primary function is case
         management.

        Returns:
            bool: Active state
        """
        return self.status != Status.INACTIVE

    @active.setter
    def active(self, value: bool) -> None:
        """
        setter for `Rescue.active`

        Args:
            value (bool): state to set `active` to.

        Returns:
            None
        """
        if isinstance(value, bool):
            if value:
                self.status = Status.OPEN
            else:
                self.status = Status.INACTIVE
            self._modified_attrs.add("active")
        else:
            raise ValueError(f"expected bool, got type {type(value)}")

    @property
    def quotes(self) -> list:
        """
        Contains all the quotes associated with this Rescue object.

        Elements of the list are Quotation objects

        Returns:
            list: list of Quotation objects
        """
        return self._quotes

    @quotes.setter
    def quotes(self, value) -> None:
        """
        Sets the value of the quotes property to whatever `value` is.

        This should not be set directly outside of case init, rather via
        `add_quote`

        Args:
            value (list): list of Quotation objects

        Returns:
            None
        """
        if isinstance(value, list):
            self._quotes = value
            self._modified_attrs.add("quotes")
        else:
            raise ValueError(f"expected type list, got {type(value)}")

    def add_quote(self, message: str, author: str or None = None) -> None:
        """
        Helper method, adds a `Quotation` object to the list.

        Use this method to add a Quotation to the Rescue

        Args:
            message (str): Message to quote
            author (str): IRC nickname of who is being quoted, if any.
            Otherwise Defaults to Mecha.

        Returns:
            None
        """
        if author:
            # set the author of the quote
            self.quotes.append(Quotation(author=author, message=message))
        else:
            # otherwise use default
            self.quotes.append(Quotation(message=message))

    @property
    def unidentified_rats(self) -> typing.List[str]:
        """
        typing.List of unidentified rats by their IRC nicknames

        Returns:
            list: unidentified rats by IRC nickname
        """
        return self._unidentified_rats

    @unidentified_rats.setter
    def unidentified_rats(self, value) -> None:
        """
        Sets the value of unidentified_rats

        Args:
            value (list): list of strings

        Raises:
            ValueError: value contained illegal types
            TypeError: value was of an illegal type

        """
        if isinstance(value, list):
            for name in value:
                if isinstance(name, str):
                    self._unidentified_rats.append(name)
                    self._modified_attrs.add("unidentified_rats")
                else:
                    raise ValueError(f"Element '{name}' expected to be of type str"
                                     f"str, got {type(name)}")
        else:
            raise TypeError(f"expected type str, got {type(value)}")

    @property
    def open(self) -> bool:
        """
        Helper method for determining if a case is considered open or not

        Returns:
            bool: is case open?

        """
        return self.status is not Status.CLOSED

    @open.setter
    def open(self, value: bool) -> None:
        """
        helper method for setting the Rescue's open status

        Args:
            value (bool): value to set

        Returns:
            None

        Raises:
            TypeError: value was not a boolean
        """
        if isinstance(value, bool):
            if value:
                self.status = Status.OPEN
            else:
                self.status = Status.CLOSED
            self._modified_attrs.add("open")
        else:
            raise TypeError(f"expected type bool, got {type(value)}")

    @property
    def epic(self) -> typing.List[Epic]:
        """
        Epic status of the rescue.

        Returns:
            Epic

        Notes:
            This property is **READ ONLY** (for now)
        """
        return self._epic

    @property
    def code_red(self) -> bool:
        """
        Code Red status for the Rescue

        Returns:
            bool
        """
        return self._code_red

    @code_red.setter
    def code_red(self, value: bool):
        if isinstance(value, bool):
            self._code_red = value
            self._modified_attrs.add("code_red")
        else:
            raise TypeError(f"expected type bool, got {type(value)}")

    @property
    def outcome(self) -> None:
        """
        Success status for Rescue.

        Returns:
            bool
        """
        return self._outcome

    @property
    def title(self) -> str or None:
        """
        The rescues operation title, if any

        Returns:
            str: operation name if set

            None: no name set.
        """
        return self._title

    @title.setter
    def title(self, value: str or None) -> None:
        """
        Set the operations title.

        Args:
            value (str or None): Operation name.

        Returns:
            None

        Raises:
            TypeError: bad value type
        """
        if value is None or isinstance(value, str):
            self._title = value
            self._modified_attrs.add("title")
        else:
            raise TypeError(f"expected type None or str, got {type(value)}")

    @property
    def marked_for_deletion(self) -> MarkForDeletion:
        """
        Mark for deletion object as used by the API

        Returns:
            dict
        """
        return self._mark_for_deletion

    @marked_for_deletion.setter
    def marked_for_deletion(self, value) -> None:
        """
        Sets the Md object

        Args:
            value (MarkForDeletion): value to set the MD object to.

        Returns:
            None

        Raises:
            TypeError: bad value type
        """
        if isinstance(value, MarkForDeletion):
            self._mark_for_deletion = value
            self._modified_attrs.add("marked_for_deletion")
        else:
            raise TypeError(f"got {type(value)} expected MarkForDeletion object")

    @property
    def rats(self) -> typing.List[Rat]:
        """
        Identified rats assigned to rescue

        Returns:
            list: identified rats by UUID
        """
        return self._rats

    @rats.setter
    def rats(self, value):
        """
        Sets the rats property directly, it is recommended to use the helper
        methods to add/remove rats.

        Args:
            value (list): new value for `rats`

        Returns:

        """
        if isinstance(value, list):
            self._rats = value
            self._modified_attrs.add("rats")

        else:
            raise TypeError(f"expected type list got {type(value)}")

    async def add_rat(self,
                      name: str = None,
                      guid: UUID or str = None,
                      rat: Rat = None) -> typing.Optional[Rat]:
        """
        Adds a rat to the rescue. This method should be run inside a `try` block, as failures will
        be raised as exceptions.

        this method will attempt to coerce `guid:str` into a UUID and may fail in
            spectacular fashion

        Args:
            rat (Rat): Existing Rat object to assign.
            name (str): name of a rat to add
            guid (UUID or str): api uuid of the rat, used if the rat is not found in the cache
                - if this is a string it will be type coerced into a UUID
        Returns:
            Rat: the added rat object

        Raises:
            ValueError: guid was of type `str` and could not be coerced.
            ValueError: Attempted to assign a Rat that does not have a UUID.

        Examples:
            ```python

            ```
        """
        assigned_rat: typing.Optional[Rat] = None

        if isinstance(rat, Rat):
            # we already have a rat object, lets verify it has an ID and assign it.
            if rat.uuid is not None:
                self.rats.append(rat)
                assigned_rat = rat
            else:
                raise ValueError("Assigned rat does not have a known API ID")

        if isinstance(name, str):
            # lets check if we already have this rat in the cache (platform, any)
            found = (await RatCache().get_rat_by_name(name, self.platform),
                     await RatCache().get_rat_by_name(name))
            if found[0]:
                self.rats.append(found[0])
                assigned_rat = found[0]
            elif found[1]:
                # a generic match (not platform specific) was found
                # TODO throw a warning so the invoking method can handle this condition
                LOG.warning("A match was found, but it was not the right platform!")
                self.rats.append(found[1])
                assigned_rat = found[1]

            else:
                # lets make a new Rat!
                # if self.rat_board:  # PRAGMA: NOCOVER
                #    pass  # TODO fetch rat from API
                # TODO: fetch rats from API handler, use that data to make a new Rat instance

                rat = Rat(name=name, uuid=guid)
                RatCache().append(rat)
                self.rats.append(rat)
                assigned_rat = rat

        elif guid is not None:
            if isinstance(guid, str):
                # attempt to coerce into a UUID
                parsed_guid = UUID(guid)
            elif isinstance(guid, UUID):
                parsed_guid = guid
            else:
                raise ValueError(f"Expected str/UUID, got {type(guid)}")

            # lets check if we already have this rat in the cache
            found = await RatCache().get_rat_by_uuid(parsed_guid)
            if found:
                self.rats.append(found)
                assigned_rat = found
            else:
                pass  # TODO: placeholder for fetching rats from the API handler

        return assigned_rat

    def mark_delete(self, reporter: str, reason: str) -> None:
        """
        Marks a rescue for deletion

        Args:
            reporter (str): person marking rescue as deleted
            reason (str): reason for the rescue being marked as deleted.

        Raises:
            TypeError: invalid params
        """
        # type enforcement
        if not isinstance(reporter, str) or not isinstance(reason, str):
            raise TypeError(f"reporter and/or reason of invalid type. got {type(reporter)},"
                            f"{type(reason)}")

        LOG.debug(f"marking rescue @{self.api_id} for deletion. reporter is {reporter} and "
                  f"their reason is '{reason}'.")
        if reason == "":
            raise ValueError("Reason required.")
        self.marked_for_deletion.reporter = reporter
        self.marked_for_deletion.reason = reason
        self.marked_for_deletion.marked = True

    def unmark_delete(self) -> None:
        """
        helper method for unmarking a rescue for deletion. resets the Md object
        """

        self.marked_for_deletion.marked = False
        self.marked_for_deletion.reason = None
        self.marked_for_deletion.reporter = None

    @contextmanager
    def change(self):
        """
        Convenience method for making safe attribute changes.

        FIXME: currently just ensures rescue.updated_at is updated.

        TODO: replace with Board context manager once its implemented

        TODO: replace current context manager with a dummy once the Board
            context manager is a thing.

        TODO: implement API integration (probably in the board Contextmanager

        Returns:
            contextManager


        Examples:
            ```

            with rescue.change():
                rescue.client = foo

            ```
        """
        yield
        self.updated_at = datetime.utcnow()

    # TODO: to/from json
    # TODO: track changes
    # TODO: helper method for adding / editing quotes
