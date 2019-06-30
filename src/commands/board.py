import logging
import typing

from src.packages.commands import command
from src.packages.context import Context
from src.packages.permissions import require_channel
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
        return await _inject_update_index(ctx, target, words)

    if target in ctx.bot.board:
        return await _inject_update_name(ctx, target, words)
    # not numeric, lets see if its a UUID or @UUID
    uuid = try_parse_uuid(target if not target.startswith('@') else target[1:])
    # if the uuid is None, or it parses successfully but does not exist in board
    if uuid and uuid not in ctx.bot.board:
        LOG.debug(f"inject invoked against a subject uuid {uuid} but it wasn't in the board")
        await ctx.reply(f"unable to find rescue @{uuid}")
        return

    if uuid:
        async with ctx.bot.board.modify_rescue(uuid) as rescue:
            rescue.add_quote(author=ctx.user.username, message=remainder(words))
            await ctx.reply(f"adding quote to rescue {rescue.board_index: <3} "
                            f"'{remainder(words)}'")
            return
    LOG.debug("nothing else fits the bill, making a new rescue...")
    # check if a platform is specified, must be the whole word
    # (prevents weirdness with words that start contain pc and friends)
    for platform_str in ("pc", "ps", "xb"):
        if platform_str in (word.casefold() for word in words):
            platform = Platforms[platform_str.upper()]
            break
    else:
        platform = None

    async with ctx.bot.board.create_rescue(client=target, platform=platform) as rescue:
        rescue: Rescue
        rescue.add_quote(message=ctx.words_eol[2], author=ctx.user.nickname)
    await ctx.reply(f"{target}'s case opened with {remainder(words)}"
                    f" ({rescue.board_index}, {rescue.platform.name if rescue.platform else ''})")


async def _inject_update_index(ctx, target, words):
    LOG.debug("first word is numerical, looking for an existing")
    index = int(target)
    if index not in ctx.bot.board:
        LOG.warning(f"unable to locate rescue by index {index}!")
        return await ctx.reply(f"unable to find rescue at index {index: <3}")

    async with ctx.bot.board.modify_rescue(index) as rescue:
        rescue.add_quote(remainder(words))
        await ctx.reply(f"{rescue.client}'s case updated with '{remainder(words)}'")


async def _inject_update_name(ctx: Context, target: str, words: typing.List[str]):
    """
    Update a existing rescue by client name

    Args:
        ctx:
        target:
        words:

    Returns:

    """
    async with ctx.bot.board.modify_rescue(target) as rescue:
        rescue: Rescue
        rescue.add_quote(message=remainder(words), author=ctx.user.username)

    await ctx.reply(f"updated {rescue.client}'s case with {remainder(words)}")


def remainder(words: typing.Iterable[str]) -> str:
    return " ".join(words)





