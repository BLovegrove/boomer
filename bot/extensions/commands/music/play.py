import discord
from discord import app_commands
from discord.ext import commands
from loguru import logger

import util.config as cfg

from util import Models, MusicHandler, VoiceHandler


class Play(commands.Cog):

    def __init__(self, bot: Models.LavaBot) -> None:
        self.bot = bot
        self.music_handler = MusicHandler(bot)
        self.voice_handler = VoiceHandler(bot)

    @app_commands.command(
        name="play",
        description=f"Plays music! Summons {cfg.bot.name} if they aren't running, adds a song to the queue if they are.",
    )
    @app_commands.describe(search="The name/artist/url of the song you want to find")
    async def play(self, itr: discord.Interaction, search: str = None):
        await itr.response.defer()
        if search:
            await self.music_handler.play(itr, search)
            return

        player = self.voice_handler.fetch_player(self.bot)

        if (player and not player.paused) or not player:
            await itr.followup.send(
                "Nothing is paused - try entering a YouTube or Soundcloud URL to play a new track instead.",
                ephemeral=True,
            )
            return

        await player.set_pause(False)
        logger.info("Player resumed")
        await itr.followup.send("Track resumed :arrow_forward:")

        return


async def setup(bot: Models.LavaBot):
    await bot.add_cog(Play(bot))
