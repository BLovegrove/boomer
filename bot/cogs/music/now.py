# ---------------------------------- Imports --------------------------------- #
import logging

import discord
from discord.ext import commands
from discord_slash import SlashContext, cog_ext
from discord_slash.utils.manage_commands import create_option

from ... import config
from ... import util
from ..core.voice import VoiceStateManager as VSM
from ..core.queue import QueueManager as QM

# ---------------------------------- Config ---------------------------------- #
cfg = config.load_config()

# --------------------------------- Cog class -------------------------------- #
class Now(commands.Cog):
    def __init__(self, bot):
        self.bot: discord.Client = bot
        self.VSM: VSM = bot.get_cog('VoiceStateManager')
        self.QM: QM = bot.get_cog('QueueManager')

    # ---------------------------------------------------------------------------- #
    #                              Methods / Commands                              #
    # ---------------------------------------------------------------------------- #

    # -------------------------------- ANCHOR NOW -------------------------------- #
    # Displays details of the current song including playtime in a handy ascii layout
    
    @cog_ext.cog_slash(
        name="now",
        description="Display info on the current song",
        guild_ids=cfg['guild_ids']
    )
    async def now(self, ctx: SlashContext):
        player = await self.VSM.ensure_voice(ctx)
        if not player:
            return
        else:
            logging.info(f"[{ctx.author.name}" + (f"#{ctx.author.discriminator}" if ctx.author.discriminator else "#0000") + f"] Fetching current song details...")

        embed = await self.QM.embed_track(
            ctx, 
            player.current, 
            "Info requested", 
            len(player.queue), 
            footer=util.seek_bar(player) + (" (paused)" if player.paused else "")
        )
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Now(bot))