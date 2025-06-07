import discord
from discord import app_commands
from discord.ext import commands
from loguru import logger

from util import models
from util.handlers.music import MusicHandler
from util.handlers.voice import VoiceHandler


class Pause(commands.Cog):

    def __init__(self, bot: models.LavaBot) -> None:
        self.bot = bot
        self.musichandler = MusicHandler(bot)
        self.voicehandler = VoiceHandler(bot)

    @app_commands.command(description="Stops the music, to be resumed later with /play")
    async def pause(self, itr: discord.Interaction):
        await itr.response.defer()
        response = await self.voicehandler.ensure_voice(itr)
        if not response.player:
            await itr.followup.send(response.message)
            return
        else:
            player = response.player

        if player.paused:
            await itr.followup.send("Already paused", ephemeral=True)

        await player.set_pause(True)
        logger.info("Player paused")
        await itr.followup.send("Track paused :pause_button:")
        return


async def setup(bot: models.LavaBot):
    await bot.add_cog(Pause(bot))
