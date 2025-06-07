import discord
import lavalink
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands
from loguru import logger

from util import models
from util.handlers.music import MusicHandler
from util.handlers.voice import VoiceHandler


class Filter(commands.Cog):

    def __init__(self, bot: models.LavaBot) -> None:
        self.bot = bot
        self.musichandler = MusicHandler(bot)
        self.voicehandler = VoiceHandler(bot)

    @app_commands.command(
        description="Adds filters to your songs - bare in mind it can take a few seconds for the filter to kick in!"
    )
    @app_commands.describe(type="Choose your filter type")
    @app_commands.choices(
        type=[
            Choice(name="Nightcore", value="nightcore"),
            Choice(name="Vibrato", value="vibrato"),
            Choice(name="Bassboost", value="bassboost"),
            Choice(name="Reset", value="reset"),
        ]
    )
    async def filter(self, itr: discord.Interaction, type: str):
        await itr.response.defer()

        response = await self.voicehandler.ensure_voice(itr)
        if not response.player:
            await itr.followup.send(response.message)
            return
        else:
            player = response.player

        await player.clear_filters()

        match (type):
            case "nightcore":
                nightcore = lavalink.filters.Timescale()
                nightcore.update(speed=1.2, pitch=1.2)
                await player.set_filter(nightcore)

            case "vibrato":
                vibrato = lavalink.filters.Vibrato()
                vibrato.update(frequency=10, depth=1)
                await player.set_filter(vibrato)

            case "bassboost":
                bassboost = lavalink.filters.Equalizer()
                bassboost.update(bands=[(2, 0.8), (3, 0.8), (4, 0.8), (5, 0.8)])
                await player.set_filter(bassboost)

            case "reset":
                await player.clear_filters()
                await itr.followup.send("Cleared all filters!")
                return

        await itr.followup.send(f"{type.capitalize()} filter applied!")
        return


class Reverb(lavalink.Filter):
    def __init__(self, length: float = 0.3, decay: float = 0.5):
        super().__init__([length, decay], True)
        self.length = decay
        self.decay = decay

    def update(self, length: float = None, decay: float = None):
        if length:
            self.length = length
        if decay:
            self.decay = decay
        return

    def serialize(self):
        return {"echo": {"echoLength": self.length, "decay": self.decay}}


async def setup(bot: models.LavaBot):
    await bot.add_cog(Filter(bot))
