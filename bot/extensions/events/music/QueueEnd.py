import lavalink
from discord.ext import commands
from loguru import logger

import util.config as cfg

from util import Models, DBHandler, MusicHandler, QueueHandler, VoiceHandler


class OnQueueEnd(commands.Cog):

    def __init__(self, bot: Models.LavaBot) -> None:
        self.bot = bot
        self.voice_handler = VoiceHandler(bot)
        self.music_handler = MusicHandler(bot)
        self.queue_handler = QueueHandler(bot, self.voice_handler)
        self.dbhandler = DBHandler(self.bot.db)

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
            await self.voice_handler.cleanup(self.bot, player)

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


async def setup(bot: Models.LavaBot):
    await bot.add_cog(OnQueueEnd(bot))
