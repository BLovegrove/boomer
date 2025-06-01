import discord
from discord.ext import commands
from loguru import logger


from util.handlers.voice import VoiceHandler
from util.models import LavaBot


class OnVoiceStateUpdate(commands.Cog):

    def __init__(self, bot: LavaBot) -> None:
        self.bot = bot
        self.voice_handler = VoiceHandler(bot)

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ):
        logger.debug("VoiceStateUpdate fired!")

        if not before.channel or after.channel:
            return

        channel = before.channel
        voice_client: discord.VoiceClient = member.guild.voice_client

        if member.guild.get_member(self.bot.user.id) not in channel.members:
            return

        if voice_client is not None and len(voice_client.channel.members) == 1:
            await voice_client.disconnect()


async def setup(bot: LavaBot):
    await bot.add_cog(OnVoiceStateUpdate(bot))
