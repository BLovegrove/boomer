# ---------------------------------- Imports --------------------------------- #
import logging

import discord
from discord.ext import commands
from discord_slash import SlashContext, cog_ext
from discord_slash.utils.manage_commands import create_option

from ... import config
from ..core.music import Music

# ---------------------------------- Config ---------------------------------- #
cfg = config.load_config()

# --------------------------------- Cog class -------------------------------- #
class Play(commands.Cog):
    def __init__(self, bot):
        self.bot: discord.Client = bot
        self.Music: Music = bot.get_cog('Music')

    # ---------------------------------------------------------------------------- #
    #                              Methods / Commands                              #
    # ---------------------------------------------------------------------------- #
    
    # -------------------------------- ANCHOR PLAY ------------------------------- #
    # Calls self.play and passes along song request / message context

    @cog_ext.cog_slash(
        name="play",
        description="Plays a song from given query / url.",
        guild_ids=cfg['guild_ids'],
        options=[
            create_option(
                name="song",
                description="Searches for a song on YouTube. Plays URL directly if given",
                option_type=str,
                required=True
            )
        ]
    )
    async def play(self, ctx: SlashContext, song: str):
        await self.Music.play(ctx, song)

def setup(bot):
    bot.add_cog(Play(bot))
