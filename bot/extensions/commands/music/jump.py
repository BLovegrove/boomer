import discord
from discord import app_commands
from discord.ext import commands

from util import Models, MusicHandler


class Jump(commands.Cog):
    def __init__(self, bot: Models.LavaBot) -> None:
        self.bot = bot
        self.music_handler = MusicHandler(bot)

    @app_commands.command(description="Skips next song in queue by default.")
    @app_commands.describe(index="The number in the queue you want to skip to")
    async def jump(self, itr: discord.Interaction, index: int = None):
        await itr.response.defer()
        await self.music_handler.skip(itr, index if index != None else 1, False)

        return


async def setup(bot: Models.LavaBot):
    await bot.add_cog(Jump(bot))
