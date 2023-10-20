import lavalink
from discord.ext import commands
from loguru import logger

from ...handlers.presence import PresenceHandler
from ...util.models import LavaBot


class TrackStart(commands.Cog):
    def __init__(self, bot: LavaBot) -> None:
        self.bot = bot

    @lavalink.listener(lavalink.events.TrackStartEvent)
    async def track_hook(self, event: lavalink.events.TrackStartEvent):
        logger.debug("TrackStart event fired!")

        player: lavalink.DefaultPlayer = event.player
        await PresenceHandler.update_status(self.bot, player)


async def setup(bot: LavaBot):
    await bot.add_cog(TrackStart(bot))
