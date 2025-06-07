import discord
from discord import app_commands
from discord.ext import commands

from util import models
from util.handlers.embed import EmbedHandler
from util.handlers.voice import VoiceHandler


class Now(commands.Cog):
    def __init__(self, bot: models.LavaBot) -> None:
        self.bot = bot
        self.voicehandler = VoiceHandler(bot)

    @app_commands.command(
        description="Shows info about the current song! Playtime, title, thumbnail, link, etc."
    )
    async def now(self, itr: discord.Interaction):
        await itr.response.defer()

        response = await self.voicehandler.ensure_voice(itr)
        if not response.player:
            await itr.followup.send(response.message)
            return
        else:
            player = response.player

        embed = EmbedHandler.Progress(itr, player).construct()

        await itr.followup.send(embed=embed)
        return


async def setup(bot: models.LavaBot):
    await bot.add_cog(Now(bot))
