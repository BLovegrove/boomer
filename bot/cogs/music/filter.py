import discord
import lavalink
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands
from loguru import logger

from ...handlers.music import MusicHandler
from ...handlers.voice import VoiceHandler
from ...util.models import LavaBot


class Filter(commands.Cog):
    def __init__(self, bot: LavaBot) -> None:
        self.bot = bot
        self.music_handler = MusicHandler(bot)
        self.voice_handler = VoiceHandler(bot)

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
    async def filter(self, interaction: discord.Interaction, type: str):
        player = await self.voice_handler.ensure_voice(interaction)

        await interaction.response.defer()

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
                # bassboost.update(band=4, gain=1.0)
                await player.set_filter(bassboost)

            case "reset":
                await player.clear_filters()
                await interaction.followup.send("Cleared all filters!")
                return

        await interaction.followup.send(f"{type.capitalize()} filter applied!")
        return


async def setup(bot: LavaBot):
    await bot.add_cog(Filter(bot))
