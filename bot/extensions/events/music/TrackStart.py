import lavalink
from discord.ext import commands
from loguru import logger

from util import models
from util.handlers.presence import PresenceHandler


class OnTrackStart(commands.Cog):

    def __init__(self, bot: models.LavaBot) -> None:
        self.bot = bot

    @lavalink.listener(lavalink.events.TrackStartEvent)
    async def track_hook(self, event: lavalink.events.TrackStartEvent):
        logger.debug("TrackStart event fired!")

        player: lavalink.DefaultPlayer = event.player
        await PresenceHandler.update_status(self.bot, player)


async def setup(bot: models.LavaBot):
    await bot.add_cog(OnTrackStart(bot))
