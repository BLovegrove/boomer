import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View

import config as cfg

from ...handlers.embeds import FavsEmbedBuilder
from ...handlers.music import MusicHandler
from ...handlers.voice import VoiceHandler
from ...util.models import LavaBot


class Favs(commands.Cog):
    def __init__(self, bot: LavaBot) -> None:
        self.bot = bot
        self.music_handler = MusicHandler(bot)
        self.voice_handler = VoiceHandler(bot)

    @app_commands.command(
        description="Let's you pick form the some of the server's favorite tunes."
    )
    @app_commands.describe(song="The favorite you're like to queue up.")
    @app_commands.choices(choices=cfg.player.favs)
    async def jump(self, interaction: discord.Interaction, index: int = None):
        await self.music_handler.skip(interaction, index if index != None else 1, False)

        return


async def setup(bot: LavaBot):
    await bot.add_cog(Favs(bot))
