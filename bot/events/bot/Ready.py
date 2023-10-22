import discord
from discord.ext import commands

import config as cfg

from ...handlers.presence import PresenceHandler
from ...handlers.voice import VoiceHandler
from ...util.models import LavaBot


class Ready(commands.Cog):
    def __init__(self, bot: LavaBot) -> None:
        self.bot = bot
        self.voice_handler = VoiceHandler(bot)

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.update_lavalink()
        try:
            guild_obj = discord.Object(id=cfg.guild.id)
            self.bot.tree.copy_global_to(guild=guild_obj)
            synced = await self.bot.tree.sync(guild=guild_obj)
            await PresenceHandler.update_status(self.bot)
        except Exception as e:
            return


async def setup(bot: LavaBot):
    await bot.add_cog(Ready(bot))
