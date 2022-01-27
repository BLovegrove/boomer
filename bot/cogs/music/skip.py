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
class Skip(commands.Cog):
    def __init__(self, bot):
        self.bot: discord.Client = bot
        self.VSM: VSM = bot.get_cog('VoiceStateManager')

    # ---------------------------------------------------------------------------- #
    #                              Methods / Commands                              #
    # ---------------------------------------------------------------------------- #

    # -------------------------------- ANCHOR SKIP ------------------------------- #
    # Skip current song or to a specific song in queue with the optional 'index' 
    # value.

    @cog_ext.cog_slash(
        name="skip",
        description="Skips current track.",
        guild_ids=cfg['guild_ids'],
        options=[
            create_option(
                name="index",
                description="Specify place in queue to skip to.",
                option_type=int,
                required=False
            )
        ]
    )
    async def skip_command(self, ctx: SlashContext, index: int=None):
        player = await self.VSM.ensure_voice(ctx)
        if not player:
            return
        
        if index:
            await self.skip(ctx, player, index=index)

        else:
            await self.skip(ctx, player)

def setup(bot):
    bot.add_cog(Skip(bot))