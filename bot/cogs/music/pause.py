import discord
from discord import app_commands
from discord.ext import commands
from loguru import logger

from ...handlers.music import MusicHandler
from ...handlers.voice import VoiceHandler
from ...util.models import LavaBot


class Pause(commands.Cog):
    def __init__(self, bot: LavaBot) -> None:
        self.bot = bot
        self.music_handler = MusicHandler(bot)
        self.voice_handler = VoiceHandler(bot)

    @app_commands.command(description="Stops the music, to be resumed later with /play")
    async def pause(self, interaction: discord.Interaction):

        player = await self.voice_handler.ensure_voice(interaction)

        if player.paused:
            await interaction.response.send_message("Already paused", ephemeral=True)

        await player.set_pause(True)
        logger.info("Player paused")
        await interaction.response.send_message("Track paused :pause_button:")
        return


async def setup(bot: LavaBot):
    await bot.add_cog(Pause(bot))
