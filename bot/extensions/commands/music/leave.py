import discord
import lavalink
from discord import app_commands
from discord.ext import commands

from util import cfg, models
from util.handlers.voice import VoiceHandler
from util.handlers.queue import QueueHandler


class Leave(commands.Cog):
    def __init__(self, bot: models.LavaBot) -> None:
        self.bot = bot
        self.voicehandler = VoiceHandler(bot)
        self.queuehandler = QueueHandler(self.bot)

    @app_commands.command(
        description=f"Requests {cfg.bot.name} to leave your voice channel and stop playing.",
    )
    async def leave(self, itr: discord.Interaction):
        await itr.response.defer()

        response = await self.voicehandler.ensure_voice(itr)
        if not response.player:
            await itr.followup.send(response.message)
            return
        else:
            player = response.player

        await self.queuehandler.clear(player)
        self.queuehandler.update_pages(player)
        await self.voicehandler.cleanup(self.bot, player)

        await itr.followup.send(f"Leaving <#{itr.user.voice.channel.id}>")


async def setup(bot: models.LavaBot):
    await bot.add_cog(Leave(bot))
