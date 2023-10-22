import discord
import lavalink
from discord import app_commands
from discord.ext import commands

import config as cfg

from ...handlers.voice import VoiceHandler
from ...util.models import LavaBot


class Join(commands.Cog):
    def __init__(self, bot: LavaBot) -> None:
        self.bot = bot
        self.voice_handler = VoiceHandler(bot)

    @app_commands.command(
        description=f"Summons {cfg.bot.name} to your voice channel and plays the summoners idle tune.",
    )
    async def join(self, inter: discord.Interaction):
        await inter.response.defer()
        player = await self.voice_handler.ensure_voice(inter)
        if not player:
            return

        await inter.followup.send(content=f"Joined <#{inter.user.voice.channel.id}>")
        await player.set_volume(cfg.player.volume_default)
        await self.bot.lavalink._dispatch_event(lavalink.events.QueueEndEvent(player))
        return


async def setup(bot: LavaBot):
    await bot.add_cog(Join(bot))
