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
class Jump(commands.Cog):
    def __init__(self, bot):
        self.bot: discord.Client = bot
        self.VSM: VSM = bot.get_cog('VoiceStateManager')

    # ---------------------------------------------------------------------------- #
    #                              Methods / Commands                              #
    # ---------------------------------------------------------------------------- #

    # -------------------------------- ANCHOR JUMP ------------------------------- #
    # Jumps ahead to a specific index in the queue and when finished playing resumes
    # the normal queue

    @cog_ext.cog_slash(
        name="jump",
        description="Jumps to a specific song in the queue and resumes normal play afterward.",
        guild_ids=cfg['guild_ids'],
        options=[
            create_option(
                name="index",
                description="The specific song to jump to. Use /list to find this.",
                option_type=int,
                required=True
            )
        ]
    )
    async def jump(self, ctx: SlashContext, index: int):
        player = await self.VSM.ensure_voice(ctx)
        if not player:
            return

        await self.skip(ctx, player, index, trim_queue=False)

def setup(bot):
    bot.add_cog(Jump(bot))