# ---------------------------------- Imports --------------------------------- #
import logging
import math

import discord
from discord.ext import commands
from discord_slash import SlashContext, cog_ext
from discord_slash.utils.manage_commands import create_option

from ... import config
from ... import util
from ..core.voice import VoiceStateManager as VSM

# ---------------------------------- Config ---------------------------------- #
cfg = config.load_config()

# --------------------------------- Cog class -------------------------------- #
class Volume(commands.Cog):
    def __init__(self, bot):
        self.bot: discord.Client = bot
        self.VSM: VSM = bot.get_cog('VoiceStateManager')

    # ---------------------------------------------------------------------------- #
    #                              Methods / Commands                              #
    # ---------------------------------------------------------------------------- #

    # ------------------------------- ANCHOR VOLUME ------------------------------ #
    # Print volume, or ncrease / decrease volume. Capped at 0-50 (displayed as 0-100)
    # for normal users and 0-1000 for the server owner.

    @cog_ext.cog_slash(
        name="volume",
        description="See Boomer's volume level. Add level to change it.",
        guild_ids=cfg['guild_ids'],
        options=[
            create_option(
                name="level",
                description="Volume level from 0% to 100%",
                option_type=int,
                required=False
            )
        ]
    )
    async def volume(self, ctx: SlashContext, level: int = None):
        player = await self.VSM.ensure_voice(ctx)
        volume = level # Make dealing with volume more sensible
        if not player:
            return

        if volume:
            if ctx.author.id != cfg['owner_id']:
                volume = util.clamp(volume, 0, 100)
                await player.set_volume(math.ceil(volume / 2))
            else:
                await player.set_volume(volume)

            logging.info(f"[{ctx.author.name}" + (f"#{ctx.author.discriminator}" if ctx.author.discriminator else "#0000") + f"] Set volume to {volume}.")

        else:
            volume = player.volume

        if volume <= 33:
            volume_emote = ":speaker:"
        elif volume > 33 and volume <= 66:
            volume_emote = ":sound:"
        else:
            volume_emote = ":loud_sound:"

        await ctx.send(f"{volume_emote} Volume is set to {volume}%")

def setup(bot):
    bot.add_cog(Volume(bot))