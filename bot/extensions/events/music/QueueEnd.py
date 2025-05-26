import lavalink
from discord.ext import commands
from loguru import logger

import util.config as cfg

from util.handlers.music import MusicHandler
from util.handlers.queue import QueueHandler
from util.handlers.voice import VoiceHandler
from util.models import LavaBot


class QueueEnd(commands.Cog):

    def __init__(self, bot: LavaBot) -> None:
        self.bot = bot
        self.voice_handler = VoiceHandler(bot)
        self.music_handler = MusicHandler(bot)
        self.queue_handler = QueueHandler(bot, self.voice_handler)

    @lavalink.listener(lavalink.events.QueueEndEvent)
    async def track_hook(self, event: lavalink.events.QueueEndEvent):
        logger.debug("Queue end event fired!")

        # TODO: Followup on issue report so theres no need to manually type player.node
        player: lavalink.DefaultPlayer = event.player
        # await player.set_volume(cfg.player.volume_idle) # TODO

        # channel = self.bot.get_guild(player.guild_id).get_channel(cfg.bot.music_channel)
        channel_id = player.fetch("last_channel")
        channel = self.bot.get_channel(channel_id)
        logger.debug(f"Found channel '{channel}' for player")

        summoner_id: int = player.fetch("summoner_id")

        bgm_url = "https://soundcloud.com/closedonsundayy/201016-star-wars-lofi-mix-1-hour?in=8vukqpvbefqi/sets/no1"
        # logger.debug(
        #     f"DatabaseHandler got '{bgm_url}' for bgm_url when checking summoners bgm prefs"
        # )

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


async def setup(bot: LavaBot):
    await bot.add_cog(QueueEnd(bot))
