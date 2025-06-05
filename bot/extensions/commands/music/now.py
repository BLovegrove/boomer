import discord
from discord import app_commands
from discord.ext import commands

from util.handlers.embed import ProgressEmbedBuilder
from util.handlers.voice import VoiceHandler
from util.models import LavaBot


class Now(commands.Cog):
    def __init__(self, bot: LavaBot) -> None:
        self.bot = bot
        self.voice_handler = VoiceHandler(bot)

    @app_commands.command(
        description="Shows info about the current song! Playtime, title, thumbnail, link, etc."
    )
    async def now(self, inter: discord.Interaction):
        await inter.response.defer()

        player = await self.voice_handler.ensure_voice(inter)
        embed = ProgressEmbedBuilder(inter, player).construct()

        await inter.followup.send(embed=embed)
        return


async def setup(bot: LavaBot):
    await bot.add_cog(Now(bot))
