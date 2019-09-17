import functools
import io
import itertools
import logging
import typing

from src.commands._list_flags import ListFlags
from src.commands._shared import coerce_rescue_type
from src.packages.board import BOARD_KEY_TYPE
from src.packages.commands import command
from src.packages.context import Context
from src.packages.permissions import require_channel, require_permission, RAT
from src.packages.rescue import Rescue
from src.packages.utils import Platforms
from src.packages.utils.ratlib import try_parse_uuid

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
        ...  # use above defaults (done this way so else can be used below as an error state)

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
    format_specifiers = "c"
    if flags.show_assigned_rats:
        format_specifiers += 'r'
    if flags.show_uuids:
        format_specifiers += '@'

    if not active_rescues:
        await ctx.reply("No active rescues.")
    else:

        output = _list_rescue(active_rescues, format_specifiers)
        if output:
            await ctx.reply(output)
    if flags.show_inactive:
        if not inactive_rescues:
            return await ctx.reply("No inactive rescues.")

        output = _list_rescue(inactive_rescues, format_specifiers)
        if output:
            await ctx.reply(output)


def _list_rescue(rescue_collection, format_specifiers):
    buffer = io.StringIO()
    buffer.write(f"{len(rescue_collection):3} active cases. ")
    for rescue in rescue_collection:
        buffer.write(format(rescue, format_specifiers))
        buffer.write('\n')
    output = buffer.getvalue()
    return output.rstrip('\n')


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

    if platform_filter:  # if we rae filtering on platform
        filters.append(rescue.platform is platform_filter)
    return not all(filters)


@require_permission(RAT)
@require_channel
@command('active', 'activate', 'inactive', 'deactivate')
async def cmd_active(ctx: Context):
    if not len(ctx.words) == 2:
        raise RuntimeError("usage error")  # TODO proper usage errors

    _, target = ctx.words

    target = coerce_rescue_type(target)

    if target not in ctx.bot.board:
        return await ctx.reply(f"Unable to find rescue by key '{target}'. Check your spelling.")

    async with ctx.bot.board.modify_rescue(target) as rescue:  # type: Rescue
        rescue.active = not rescue.active

    await ctx.reply(f"{rescue.client}'s case is now {'active' if rescue.active else 'inactive'}")


@require_permission(RAT)
@require_channel
@command("clear", "close")
async def cmd_close(ctx: Context):
    """
    clear a case
     TODO: complete docstring
    Args:
        ctx:

    Returns:

    """

    # unpacking word list into targets
    _, raw_rescue_target, *remaining_words = ctx.words
    if remaining_words:
        raw_rat_target, *remaining_words = remaining_words
    else:
        raw_rat_target = None

    LOG.debug(f"rescue target:= {raw_rescue_target}")
    LOG.debug(f"rat target:= {raw_rat_target}")
    LOG.debug(f"remainder:= {remaining_words}")
    if remaining_words:
        raise RuntimeError("usage error")  # TODO proper usage errors

    # convert the specified rescue argument into a key for lookup
    rescue_key = coerce_rescue_type(raw_rescue_target)
    if rescue_key not in ctx.bot.board:
        # not a tracked rescue, bail out
        return await ctx.reply("Could not find a case with that name or number.")

    # get the client's name before we close the rescue
    client = ctx.bot.board[rescue_key].client
    await ctx.bot.board.close_rescue(rescue_key)
    await ctx.reply(f"Case {client} got cleared! ")
