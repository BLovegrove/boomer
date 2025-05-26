import discord
from discord import app_commands
from discord.ext import commands

from ...handlers.music import MusicHandler
from ...handlers.voice import VoiceHandler
from ...util.models import LavaBot


class Jump(commands.Cog):
    def __init__(self, bot: LavaBot) -> None:
        self.bot = bot
        self.music_handler = MusicHandler(bot)
        # self.voice_handler = VoiceHandler(bot)

    @app_commands.command(description="Skips next song in queue by default.")
    @app_commands.describe(index="The number in the queue you want to skip to")
    async def jump(self, interaction: discord.Interaction, index: int = None):

        await self.music_handler.skip(interaction, index if index != None else 1, False)

        return


async def setup(bot: LavaBot):
    await bot.add_cog(Jump(bot))
