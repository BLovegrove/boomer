import lavalink
from discord.ext import commands
from loguru import logger

from util.handlers.voice import VoiceHandler
from util.models import LavaBot


class OnWebSocketClosed(commands.Cog):
    def __init__(self, bot: LavaBot) -> None:
        self.bot = bot
        self.voice_handler = VoiceHandler(bot)

    @lavalink.listener(lavalink.events.WebSocketClosedEvent)
    async def track_hook(self, event: lavalink.events.WebSocketClosedEvent):
        logger.debug("WebSocketClosed event fired!")

        player: lavalink.DefaultPlayer = event.player

        await self.voice_handler.cleanup(self.bot, player)

        return


async def setup(bot: LavaBot):
    await bot.add_cog(OnWebSocketClosed(bot))
