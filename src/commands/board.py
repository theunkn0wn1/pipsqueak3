import logging

from src.packages.commands import command
from src.packages.context import Context
from src.packages.permissions import require_permission, RAT, require_channel
from src.packages.rescue import Rescue

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

    if ctx.words[1].isnumeric():
        # first argument is numeric, parse it into an integer (should be safe due to .isnumeric)
        LOG.debug("first word is numerical, looking for an existing")
        index = int(ctx.words[1])
        if index not in ctx.bot.board:
            LOG.warning(f"unable to locate rescue by index {index}!")
            await ctx.reply(f"unable to find rescue at index {index: <3}")
            async with ctx.bot.board.create_rescue(client=ctx.words[2]) as rescue:
                rescue: Rescue
                rescue.add_quote(message=ctx.words_eol[3], author=ctx.user.nickname)
            await ctx.reply("created rescue")


@command("debug_list")
async def cmd_debug_list(ctx: Context):
    for rescue in ctx.bot.board.values():
        await ctx.reply(f"rescue #{rescue.board_index:0>3} for user {rescue.client} ...")
    else:
        await ctx.reply("no rescues found.")
