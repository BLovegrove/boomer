import discord
from discord.ext import commands
from loguru import logger

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
        logger.info(f"Bot is logged in as {self.bot.user}")
        logger.info("Syncing slash commands...")
        try:
            guild_obj = discord.Object(id=cfg.guild.id)
            self.bot.tree.copy_global_to(guild=guild_obj)
            synced = await self.bot.tree.sync(guild=guild_obj)
            logger.info(f"Synced {len(synced)} commands.")
            await PresenceHandler.update_status(self.bot)
        except Exception as e:
            logger.exception("Error while syncing slash commands.")
            return


async def setup(bot: LavaBot):
    await bot.add_cog(Ready(bot))
