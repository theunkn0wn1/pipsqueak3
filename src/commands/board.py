import logging

from src.packages.commands import command
from src.packages.context import Context
from src.packages.permissions import require_permission, RAT, require_channel
from src.packages.rescue import Rescue
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

    # !inject {target} {words} {*words}
    _, target, *words = ctx.words
    LOG.debug(f"in inject, target := {target}")
    if target.isnumeric():
        # first argument is numeric, parse it into an integer (should be safe due to .isnumeric)
        LOG.debug("first word is numerical, looking for an existing")
        index = int(target)
        if index not in ctx.bot.board:
            LOG.warning(f"unable to locate rescue by index {index}!")
            await ctx.reply(f"unable to find rescue at index {index: <3}")
            return  # bail out
        async with ctx.bot.board.modify_rescue(index) as rescue:
            rescue.add_quote(" ".join(words))
            await ctx.reply(f"{rescue.client}'s case updated with '{' '.join(words)}'")
            return

    # not numeric, lets see if its a UUID or @UUID
    uuid = try_parse_uuid(target if not target.startswith('@') else target[1:])
    # if the uuid is None, or it parses successfully but does not exist in board
    if uuid and uuid not in ctx.bot.board:
        LOG.debug(f"inject invoked against a subject uuid {uuid} but it wasn't in the board")
        await ctx.reply(f"unable to find rescue @{uuid}")
        return

    if uuid:
        async with ctx.bot.board.modify_rescue(uuid) as rescue:
            rescue.add_quote(author=ctx.user.username, message=" ".join(words))
            await ctx.reply(f"adding quote to rescue {rescue.board_index: <3} "
                            f"'{' '.join(words)}'")
            return
    LOG.debug("nothing else fits the bill, making a new rescue...")
    async with ctx.bot.board.create_rescue(client=target) as rescue:
        rescue: Rescue
        rescue.add_quote(message=ctx.words_eol[2], author=ctx.user.nickname)
    await ctx.reply(f"{target}'s case opened with {ctx.words_eol[2]}")


@command("debug_list")
async def cmd_debug_list(ctx: Context):
    for rescue in ctx.bot.board.values():
        await ctx.reply(
            f"rescue #{rescue.board_index:0>3} for user {rescue.client} (@{rescue.api_id})")
    else:
        await ctx.reply("no rescues found.")
