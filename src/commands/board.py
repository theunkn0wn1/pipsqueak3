import io
import logging
import typing
from dataclasses import dataclass
import functools
import itertools

from src.packages.commands import command
from src.packages.context import Context
from src.packages.permissions import require_channel
from src.packages.rescue import Rescue
from src.packages.utils import Platforms
from src.packages.utils.ratlib import try_parse_uuid
from src.packages.board import BOARD_KEY_TYPE

LOG = logging.getLogger(f"mecha.{__name__}")


@command("inject")
@require_channel
# @require_permission(RAT)
async def cmd_inject(ctx: Context):
    """
    inject handling

    Args:
        ctx:

    """
    if len(ctx.words) < 3:  # prefix case user [...]
        ...  # FIXME : invalid usage
        await ctx.reply("Invalid usage.")
        return

        # !inject {target} {words} {*words}
    _, target, *words = ctx.words
    LOG.debug(f"in inject, target := {target}")
    if target.isnumeric():
        # first argument is numeric, parse it into an integer (should be safe due to .isnumeric)
        LOG.debug("first word is numerical, looking for an existing")
        index = int(target)
        if index not in ctx.bot.board:
            LOG.warning(f"unable to locate rescue by index {index}!")
            return await ctx.reply(f"unable to find rescue at index {index: <3}")
        return await _inject_do_update(ctx, int(target), remainder(words))

    if target in ctx.bot.board:
        return await _inject_do_update(ctx, target, remainder(words))
    # not numeric, lets see if its a UUID or @UUID
    uuid = try_parse_uuid(target if not target.startswith('@') else target[1:])
    # if the uuid is None, or it parses successfully but does not exist in board
    if uuid and uuid not in ctx.bot.board:
        LOG.debug(f"inject invoked against a subject uuid {uuid} but it wasn't in the board")
        await ctx.reply(f"unable to find rescue @{uuid}")
        return

    if uuid:
        return await _inject_do_update(ctx, uuid, payload=remainder(words))

    LOG.debug("nothing else fits the bill, making a new rescue...")
    # check if a platform is specified, must be the whole word
    # (prevents weirdness with words that start contain pc and friends)
    for platform_str in ("pc", "ps", "xb", "xbox"):
        if platform_str in (word.casefold() for word in words):
            platform = Platforms[platform_str.upper()[:2]]
            break
    else:
        platform = None

    async with ctx.bot.board.create_rescue(client=target, platform=platform) as rescue:
        rescue: Rescue
        rescue.add_quote(message=ctx.words_eol[2], author=ctx.user.nickname)
    await ctx.reply(f"{target}'s case opened with {remainder(words)}"
                    f" ({rescue.board_index}, {rescue.platform.name if rescue.platform else ''})")


async def _inject_do_update(ctx: Context, target: BOARD_KEY_TYPE, payload: str):
    """
    Do the actual quote append thing

    Args:
        ctx: execution context
        target: subject of the inject
        words: remaining unparsed words in the inject
    """
    async with ctx.bot.board.modify_rescue(target) as rescue:
        rescue: Rescue
        rescue.add_quote(message=payload, author=ctx.user.username)

    await ctx.reply(f"updated {rescue.client}'s case with {payload}")


def remainder(words: typing.Iterable[str]) -> str:
    return " ".join(words)


@command("list")
async def cmd_list(ctx: Context):
    """
    Implementation of !list

        Supported parameters:
        -i: Also show inactive (but still open) cases.
        -r: Show assigned rats
        -u: Show only cases with no assigned rats
        -@: Show full case IDs.  (LONG)

    Args:
        ctx:

    """
    _, *words = ctx.words

    flags = ListFlags()
    platform_filter = None

    # plain invocation
    if len(words) == 0:
        show_inactive = False
        show_assigned_rats = False
        only_unassigned_rescues = False
        full_uuids = False


    # arguments invocation
    elif len(words) == 1 or len(words) == 2:
        flags_set = False
        platform_filter_set = False

        for word in words:  # type: str
            if word.startswith('-'):
                if flags_set:
                    raise RuntimeError("invalid usage")  # FIXME: usage warning to user
                flags = ListFlags.from_word(word)
                flags_set = True
            else:
                # platform or bust
                if platform_filter_set:
                    raise RuntimeError("invalid usage")  # FIXME: usage error

                try:
                    platform_filter = Platforms[word.upper()]
                except KeyError:
                    return await ctx.reply(f"unrecognized platform '{word.upper()}'")

    else:
        raise RuntimeError  # FIXME: usage error
    LOG.debug(f"flags set:= {flags} \t platform_filter := {platform_filter}")
    active_rescues: typing.List[Rescue] = []
    inactive_rescues: typing.List[Rescue] = []

    rescue_filter = functools.partial(_rescue_filter, flags, platform_filter)

    # for each rescue that doesn't matches the filter
    for rescue in itertools.filterfalse(rescue_filter, iter(ctx.bot.board.values())):  # type: Rescue
        # put it in the right list
        if rescue.active:
            active_rescues.append(rescue)
        else:
            inactive_rescues.append(rescue)

    if not active_rescues:
        await ctx.reply("No active rescues.")

    format_specifiers = "c"
    if flags.show_assigned_rats:
        format_specifiers += 'a'
    if flags.show_uuids:
        format_specifiers += '@'

    buffer = io.StringIO(f"{len(active_rescues): <3} active cases, ")
    for rescue in active_rescues:
        buffer.write(format(rescue, format_specifiers))
        buffer.write('\n')
    await ctx.reply(buffer.getvalue())
    if flags.show_inactive:
        if not inactive_rescues:
            await ctx.reply("No inactive rescues.")


@dataclass(frozen=True)
class ListFlags:
    show_inactive: bool = False
    filter_unassigned_rescues: bool = False
    show_assigned_rats: bool = False
    show_uuids: bool = False

    @classmethod
    def from_word(cls, argument: str):
        argument = argument.casefold()

        show_inactive = "i" in argument
        """
        Show inactive rescues
        """
        show_assigned_rats = "r" in argument
        """
        Show assigned rats per rescue
        """
        filter_unassigned_rescues = "u" in argument
        """
        only show rescues without assigned rats
        """
        show_uuids = "@" in argument
        """
        show API UUIDs
        """
        return cls(show_inactive, filter_unassigned_rescues, show_assigned_rats, show_uuids)


def _rescue_filter(flags: ListFlags,
                   platform_filter: typing.Optional[Platforms],
                   rescue: Rescue) -> bool:
    """
    determine whether the `rescue` object is one we care about

    Args:
        rescue: 

    Returns:

    """
    filters = []

    if flags.filter_unassigned_rescues:
        # return whether any rats are assigned
        # either properly or via unidentified rats
        filters.append(bool(rescue.rats) or bool(rescue.unidentified_rats))

    # use the active bool on rescue if we don't want inactives, otherwise True
    filters.append(rescue.active if not flags.show_inactive else True)
    return not all(filters)
