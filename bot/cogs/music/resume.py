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
class Resume(commands.Cog):
    def __init__(self, bot):
        self.bot: discord.Client = bot
        self.VSM: VSM = bot.get_cog('VoiceStateManager')

    # ---------------------------------------------------------------------------- #
    #                              Methods / Commands                              #
    # ---------------------------------------------------------------------------- #
    
    # ------------------------------- ANCHOR RESUME ------------------------------ #
    # resumes the current track. paused with /pause

    @cog_ext.cog_slash(
        name="resume",
        description="Resumes the currently playing song. Pause with /pause.",
        guild_ids=cfg['guild_ids']
    )
    async def resume(self, ctx: SlashContext):
        player = await self.VSM.ensure_voice(ctx)
        if not player:
            return
        else:
            logging.info(f"[{ctx.author.name}" + (f"#{ctx.author.discriminator}" if ctx.author.discriminator else "#0000") + f"] Resumed track.")
        
        await player.set_pause(False)
        await ctx.send(":arrow_forward: Resumed track.")

def setup(bot):
    bot.add_cog(Resume(bot))