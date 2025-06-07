import discord
import lavalink
from discord import app_commands
from discord.ext import commands

import util.config as cfg

from util import Models, VoiceHandler


class Join(commands.Cog):
    def __init__(self, bot: Models.LavaBot) -> None:
        self.bot = bot
        self.voice_handler = VoiceHandler(bot)

    @app_commands.command(
        description=f"Summons {cfg.bot.name} to your voice channel and plays the summoners idle tune.",
    )
    async def join(self, itr: discord.Interaction):
        await self.join_voice(itr)

    async def join_voice(self, itr: discord.Interaction):
        await itr.response.defer()

        player = await self.voice_handler.ensure_voice(itr)
        if not player:
            return

        await itr.followup.send(content=f"Joined <#{itr.user.voice.channel.id}>")
        await player.set_volume(cfg.player.volume_default)
        self.bot.lavalink._dispatch_event(lavalink.events.QueueEndEvent(player))
        return


async def setup(bot: Models.LavaBot):
    await bot.add_cog(Join(bot))
