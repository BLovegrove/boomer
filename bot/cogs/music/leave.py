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
class Leave(commands.Cog):
    def __init__(self, bot):
        self.bot: discord.Client = bot
        self.VSM: VSM = bot.get_cog('VoiceStateManager')

    # ---------------------------------------------------------------------------- #
    #                              Methods / Commands                              #
    # ---------------------------------------------------------------------------- #

    # ------------------------------- ANCHOR LEAVE ------------------------------- #
    # Leave voice chat if in one. Also resets the queue and clears any modifiers.

    @cog_ext.cog_slash(
        name="leave",
        description="Disconnects Boomer from voice and clears the queue",
        guild_ids=cfg['guild_ids']
    )
    async def leave(self, ctx: SlashContext):
        player = await self.VSM.ensure_voice(ctx)
        if not player:
            return
        else:
            logging.info(f"[{ctx.author.name}" + (f"#{ctx.author.discriminator}" if ctx.author.discriminator else "#0000") + f"] Leaving channel... Cleared queue. Modifiers disabled. Volume reset to default.")

        await self.VSM.disconnect(player, ctx.guild)

        await ctx.send(f":wave: Leaving <#{player.fetch('voice').id}> and clearing queue.")

def setup(bot):
    bot.add_cog(Leave(bot))