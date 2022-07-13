# ---------------------------------- Imports --------------------------------- #
import logging

import discord
from discord.ext import commands
from discord_slash import SlashContext, cog_ext
from discord_slash.utils.manage_commands import create_option

from ... import config
from ..core.voice import VoiceStateManager as VSM

# ---------------------------------- Config ---------------------------------- #
cfg = config.load_config()

# --------------------------------- Cog class -------------------------------- #
class Repeat(commands.Cog):
    def __init__(self, bot):
        self.bot: discord.Client = bot
        self.VSM: VSM = bot.get_cog('VoiceStateManager')

    # ---------------------------------------------------------------------------- #
    #                              Methods / Commands                              #
    # ---------------------------------------------------------------------------- #

    # ------------------------------- ANCHOR REPEAT ------------------------------ #
    # Repeat either the current track or the entire playlist with a subcommand 'queue'

    # Single track
    @cog_ext.cog_subcommand(
        base="repeat",
        name="track",
        description="Repeats current song.",
        guild_ids=cfg['guild_ids']
    )
    async def loop(self, ctx: SlashContext):
        player = await self.VSM.ensure_voice(ctx)
        if not player:
            return
        else:
            logging.info(f"[{ctx.author.name}" + (f"#{ctx.author.discriminator}" if ctx.author.discriminator else "#0000") + f"] Changing repeat state...")

        if player.fetch('repeat_one'):
            player.store('repeat_one', None)
            await ctx.send(":arrow_forward: Stopped repeating track.")
            logging.info(f"Repeat once disabled.")
        else:
            track = player.current
            player.store('repeat_one', track)
            await ctx.send(":repeat_one: Current track now repeating.")
            logging.info(f"Repeat once enabled")

    # Whole queue
    @cog_ext.cog_subcommand(
        base="repeat",
        name="queue",
        description="Repeats entire queue.",
        guild_ids=cfg['guild_ids']
    )
    async def loop_queue(self, ctx: SlashContext):
        player = await self.VSM.ensure_voice(ctx)
        if not player:
            return
        else:
            logging.info(f"[{ctx.author.name}" + (f"#{ctx.author.discriminator}" if ctx.author.discriminator else "#0000") + f"] Changing repeat state...")

        player.set_repeat(not player.repeat)
        if player.repeat:
            await ctx.send(":repeat: Current queue now repeating.")
            logging.info(f"Repeat queue enabled")
        else:
            await ctx.send(":arrow_forward: Stopped repeating queue.")
            logging.info(f"Repeat queue disabled")

def setup(bot):
    bot.add_cog(Repeat(bot))