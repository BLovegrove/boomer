import discord
from discord import app_commands
from discord.ext import commands
from loguru import logger

from util import Models, MusicHandler, VoiceHandler


class Pause(commands.Cog):
    def __init__(self, bot: Models.LavaBot) -> None:
        self.bot = bot
        self.music_handler = MusicHandler(bot)
        self.voice_handler = VoiceHandler(bot)

    @app_commands.command(description="Stops the music, to be resumed later with /play")
    async def pause(self, inter: discord.Interaction):
        await inter.response.defer()
        player = await self.voice_handler.ensure_voice(inter)

        if player.paused:
            await inter.followup.send("Already paused", ephemeral=True)

        await player.set_pause(True)
        logger.info("Player paused")
        await inter.followup.send("Track paused :pause_button:")
        return


async def setup(bot: Models.LavaBot):
    await bot.add_cog(Pause(bot))
