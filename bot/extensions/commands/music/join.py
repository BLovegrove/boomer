import discord
import lavalink
from discord import app_commands
from discord.ext import commands

import util.cfg as cfg

from util import models
from util.handlers.voice import VoiceHandler
from util.handlers.queue import QueueHandler


class Join(commands.Cog):
    def __init__(self, bot: models.LavaBot) -> None:
        self.bot = bot
        self.voicehandler = VoiceHandler(self.bot)
        self.queuehandler = QueueHandler(self.bot)

    @app_commands.command(
        description=f"Summons {cfg.bot.name} to your voice channel and plays the summoners idle tune.",
    )
    async def join(self, itr: discord.Interaction):
        await self.join_voice(itr)

    async def join_voice(self, itr: discord.Interaction):
        await itr.response.defer()

        response = await self.voicehandler.ensure_voice(itr)
        if not response.player:
            await itr.followup.send(response.message)
            return
        else:
            player = response.player

        await itr.followup.send(content=f"Joined <#{itr.user.voice.channel.id}>")
        await player.set_volume(cfg.player.volume_default)
        self.bot.lavalink._dispatch_event(lavalink.events.QueueEndEvent(player))
        self.queuehandler.update_pages(player)
        return


async def setup(bot: models.LavaBot):
    await bot.add_cog(Join(bot))
