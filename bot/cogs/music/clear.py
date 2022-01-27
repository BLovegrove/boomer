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
class Clear(commands.Cog):
    def __init__(self, bot):
        self.bot: discord.Client = bot
        self.VSM: VSM = bot.get_cog('VoiceStateManager')

    # ---------------------------------------------------------------------------- #
    #                              Methods / Commands                              #
    # ---------------------------------------------------------------------------- #

    # ------------------------------- ANCHOR CLEAR ------------------------------- #
    # Clears the queue without making boomer leave the call. 

    @cog_ext.cog_slash(
        name="clear",
        description="Clears current queue.",
        guild_ids=cfg['guild_ids'],
        options=[
            create_option(
                name="index",
                description="Specify single song in queue to clear.",
                option_type=int,
                required=False
            )
        ]
    )
    async def clear_command(self, ctx: SlashContext, index: int=None):
        player = await self.VSM.ensure_voice(ctx)
        if not player:
            return
        else:
            logging.info(f"[{ctx.author.name}" + (f"#{ctx.author.discriminator}" if ctx.author.discriminator else "#0000") + f"] Clearing " + f"item with index {index}..." if index else "whole queue...")
        
        if not index:
            await self.clear(ctx)

        else:
            if index <= 0:
                await ctx.send(":warning: That index is too low! Queue starts at #1.", hidden=True)
                logging.warn(f"Index too low! Expected: >=1. Recieved: {index}")
                return

            elif index > len(player.queue):
                await ctx.send(f":warning: That index is too high! Queue only {len(player.queue)} items long.", hidden=True)
                logging.warn(f"Index too high! Expected: <= {len(player.queue)}. Recieved: {index}")
                return

            else:
                await self.clear(ctx, index - 1)

def setup(bot):
    bot.add_cog(Clear(bot))