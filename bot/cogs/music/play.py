import discord
from discord import app_commands
from discord.ext import commands
from loguru import logger

import config as cfg

from ...handlers.music import MusicHandler
from ...handlers.voice import VoiceHandler
from ...util.models import LavaBot


class Play(commands.Cog):
    def __init__(self, bot: LavaBot) -> None:
        self.bot = bot
        self.music_handler = MusicHandler(bot)
        self.voice_handler = VoiceHandler(bot)

    @app_commands.command(
        name="play",
        description=f"Plays music! Summons {cfg.bot.name} if they aren't running, adds a song to the queue if they are.",
    )
    @app_commands.describe(search="The name/artist/url of the song you want to find")
    async def play(self, inter: discord.Interaction, search: str = None):
        if search:
            # player = self.bot.lavalink.player_manager.create(interaction.guild_id)
            await self.music_handler.play(inter, search)
            return

        player = self.voice_handler.fetch_player(self.bot)

        if (player and not player.paused) or not player:
            await inter.response.send_message(
                "Nothing is paused - try entering a YouTube or Soundcloud URL to play a new track instead.",
                ephemeral=True,
            )
            return

        await player.set_pause(False)
        logger.info("Player resumed")
        await inter.response.send_message("Track resumed :arrow_forward:")

        return


async def setup(bot: LavaBot):
    await bot.add_cog(Play(bot))
