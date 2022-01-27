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
class Shuffle(commands.Cog):
    def __init__(self, bot):
        self.bot: discord.Client = bot
        self.VSM: VSM = bot.get_cog('VoiceStateManager')

    # ---------------------------------------------------------------------------- #
    #                              Methods / Commands                              #
    # ---------------------------------------------------------------------------- #

    # ------------------------------ ANCHOR SHUFFLE ------------------------------ #
    # Shuffles current queue on and off

    @cog_ext.cog_slash(
        name="shuffle",
        description="Shuffles the current queue. Works well with /repeat queue.",
        guild_ids=cfg['guild_ids']
    )
    async def shuffle(self, ctx: SlashContext):
        player = await self.VSM.ensure_voice(ctx)
        if not player:
            return
        else:
            logging.info(f"[{ctx.author.name}" + (f"#{ctx.author.discriminator}" if ctx.author.discriminator else "#0000") + f"] Changing shuffle state...")

        if player.shuffle:
            player.set_shuffle(False)
            await ctx.send(":arrow_forward: Stopped shuffling.")
            logging.info(f"Shuffle state disabled")
        else:
            player.set_shuffle(True)
            await ctx.send(":twisted_rightwards_arrows: Current queue now shuffling.")
            logging.info(f"Shuffle state enabled")

def setup(bot):
    bot.add_cog(Shuffle(bot))