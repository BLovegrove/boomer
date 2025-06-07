import lavalink
from discord.ext import commands
from loguru import logger

import util.cfg as cfg

from util import models
from util.handlers.database import DatabaseHandler
from util.handlers.music import MusicHandler
from util.handlers.voice import VoiceHandler


class OnQueueEnd(commands.Cog):

    def __init__(self, bot: models.LavaBot) -> None:
        self.bot = bot
        self.voicehandler = VoiceHandler(bot)
        self.musichandler = MusicHandler(bot)
        self.dbhandler = DatabaseHandler(self.bot.db)

    @lavalink.listener(lavalink.events.QueueEndEvent)
    async def track_hook(self, event: lavalink.events.QueueEndEvent):
        logger.debug("Queue end event fired!")

        player: lavalink.DefaultPlayer = event.player
        await player.set_volume(cfg.player.volume_idle)

        channel_id = player.fetch("last_channel")
        channel = self.bot.get_channel(channel_id)
        logger.debug(f"Found channel '{channel}' for player")

        summoner = player.fetch("summoner")

        bgm_url = self.dbhandler.get_bgm(summoner)
        if not bgm_url:
            bgm_url = cfg.player.bgm_default

        result: lavalink.LoadResult = await player.node.get_tracks(bgm_url)

        if (
            not result
            or not result.tracks
            or result.load_type != result.load_type.TRACK
        ):
            player.queue.clear()
            await self.voicehandler.cleanup(self.bot, player)

            if not player.channel_id:
                logger.warning(f"Failed to find text channel while queuing idle track.")
                return

            await channel.send(
                ":warning: Nothing found when looking for idle music! Look for a new video."
            )

            logger.debug(f"Lavalink search result: {result.tracks}")
            logger.debug(f"Lavalink search load_type: {result.load_type}")
            return

        if player.fetch("idle"):
            player.set_loop(player.LOOP_NONE)
            player.queue.clear()
            await player.skip()

        track = result.tracks[0]
        player.queue.insert(0, track)

        player.store("idle", True)
        player.set_loop(player.LOOP_SINGLE)

        if not player.is_playing:
            await player.play()


async def setup(bot: models.LavaBot):
    await bot.add_cog(OnQueueEnd(bot))
