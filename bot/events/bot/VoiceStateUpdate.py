import discord
import lavalink
from discord.ext import commands

import config as cfg

from ...handlers.voice import VoiceHandler
from ...util.models import LavaBot


class VoiceStateUpdate(commands.Cog):
    def __init__(self, bot: LavaBot) -> None:
        self.bot = bot
        self.voice_handler = VoiceHandler(bot)

    @commands.Cog.listener()
    @staticmethod
    async def on_voice_state_update(
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ):
        if not before.channel or after.channel:
            return

        channel = before.channel
        voice_client: discord.VoiceClient = member.guild.voice_client

        if member.guild.get_member(cfg.bot.id) not in channel.members:
            return

        if voice_client is not None and len(voice_client.channel.members) == 1:
            await voice_client.disconnect()


async def setup(bot: LavaBot):
    await bot.add_cog(VoiceStateUpdate(bot))
