import discord
import lavalink
from discord import app_commands
from discord.ext import commands

import util.config as cfg

from util.handlers.voice import VoiceHandler
from util.models import LavaBot


class Leave(commands.Cog):
    def __init__(self, bot: LavaBot) -> None:
        self.bot = bot
        self.voicehandler = VoiceHandler(bot)

    @app_commands.command(
        description=f"Requests {cfg.bot.name} to leave your voice channel and stop playing.",
    )
    async def leave(self, itr: discord.Interaction):
        await itr.response.defer()

        player = await self.voicehandler.ensure_voice(itr)
        if player:
            await self.voicehandler.cleanup(self.bot, player)

        await itr.followup.send(f"Leaving <#{itr.user.voice.channel.id}>")


async def setup(bot: LavaBot):
    await bot.add_cog(Leave(bot))
