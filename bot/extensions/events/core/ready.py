import discord
from discord.ext import commands
from loguru import logger

import util.config as cfg
from util import models
from util.handlers.voice import VoiceHandler


class OnReady(commands.Cog):
    def __init__(self, bot: models.LavaBot) -> None:
        self.bot = bot
        self.voice_handler = VoiceHandler(bot)

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.update_lavalink()
        logger.success(f"Bot is logged in as {self.bot.user}")

        try:
            guild_obj = discord.Object(id=cfg.bot.guild_id)
            self.bot.tree.copy_global_to(guild=guild_obj)
            synced = await self.bot.tree.sync(guild=guild_obj)
            logger.success(f"Synced {len(synced)} commands")

        except Exception as e:
            logger.exception("Error while syncing slash commands.")
            return


async def setup(bot):
    await bot.add_cog(OnReady(bot))
