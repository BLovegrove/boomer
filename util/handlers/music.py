import traceback
from typing import Union

import discord
import lavalink
from loguru import logger

from util import cfg, models
from util.handlers.embed import EmbedHandler
from util.handlers.voice import VoiceHandler
from util.handlers.queue import QueueHandler
from util.handlers.database import DatabaseHandler

__all__ = ["MusicHandler"]


class MusicHandler:
    def __init__(self, bot: models.LavaBot) -> None:
        self.bot = bot
        self.voicehandler = VoiceHandler(self.bot)
        self.queuehandler = QueueHandler(self.bot)
        self.dbhandler = DatabaseHandler(self.bot.db)

    class PlayResult:
        def __init__(
            self,
            title: str,
            tracks: list[Union[lavalink.AudioTrack, lavalink.DeferredAudioTrack]],
        ):
            self.title = title
            self.tracks = tracks

    async def load_tracks(
        self,
        player: lavalink.DefaultPlayer,
        queries: Union[str, list[str]],
    ) -> PlayResult | None:
        if isinstance(queries, str):
            queries = [queries]

        loaded = []
        title = ""

        for query in queries:

            if "https://" not in query:
                query = "ytsearch:" + query

            result = await player.node.get_tracks(query)

            try:
                match result.load_type:
                    case lavalink.LoadType.ERROR:
                        return

                    case lavalink.LoadType.EMPTY:
                        return

                    case lavalink.LoadType.SEARCH | lavalink.LoadType.TRACK:
                        loaded.append(result.tracks[0])
                        title = result.tracks[0].title

                    case lavalink.LoadType.PLAYLIST:
                        for track in result.tracks:
                            loaded.append(track)

                        title = result.playlist_info.name

                    case _:
                        logger.warning(
                            f"Load type for play request defaulted. Query '{query}' result as follows:"
                        )
                        logger.warning(result)
                        return

            except Exception as e:
                logger.error(f"Failed to get track from query: {query}")
                return

        if loaded != []:
            return self.PlayResult(title, loaded)
        else:
            return

    async def play(
        self,
        player: lavalink.DefaultPlayer,
        tracks: Union[
            str,
            list[str],
            PlayResult,
        ],
    ) -> PlayResult:

        if isinstance(tracks, self.PlayResult):
            result = tracks
        else:
            result = await self.load_tracks(player, tracks)
            if not result:
                return

        for track in result.tracks:
            player.add(track)
            logger.debug(f"Track added to queue: {track.title}")

        if player.fetch("idle"):
            player.store("idle", False)
            player.set_loop(player.LOOP_NONE)
            await player.set_volume(cfg.player.volume_default)
            await player.skip()

        elif not player.is_playing:
            await player.set_volume(cfg.player.volume_default)
            await player.play()

        self.queuehandler.update_pages(player)
        return result

    async def skip(self, itr: discord.Interaction, index: int, trim_queue: bool = True):
        response = await self.voicehandler.ensure_voice(itr)
        if not response.player:
            await itr.followup.send(response.message)
            return
        else:
            player = response.player

        logger.debug(f"Queue length: {len(player.queue)}, loop status: {player.loop}")
        if len(player.queue) == 0 and player.loop == 0:
            await itr.followup.send(
                ":notepad_spiral: End of queue - time for your daily dose of idle tunes!"
            )
            if not player.fetch("idle"):
                await player.skip()

            return

        if player.loop == 1 or (player.loop == 2 and len(player.queue) <= 1):
            next_track = player.current

            if not next_track:
                await itr.followup.send(
                    f"Error! Track not found. Something went wrong with playback - try kicking {cfg.bot.name} from the VC and trying again.",
                    ephemeral=True,
                )
                return

            embed = EmbedHandler.Skip(itr, next_track, player)
            await itr.followup.send(
                ":repeat_one: Repeat enabled - looping song.",
                embed=embed.construct(),
            )
            await player.seek(0)
            logger.debug("Skipped song (repeat enabled).")
            return

        if index < 0:
            await itr.followup.send(
                ":warning: That index is too low! Queue starts at #1.", ephemeral=True
            )
            logger.warning(
                f"Skip failed. Index too low (expected: >=1. Recieved: {index})"
            )
            return

        elif index > len(player.queue):
            await itr.followup.send(
                f":warning: That index is too high! Queue only {len(player.queue)} items long.",
                ephemeral=True,
            )
            logger.warning(
                f"Skip failed. Index too high (expected: <={len(player.queue)}. Recieved: {index})"
            )
            return

        else:
            if trim_queue:
                logger.debug(
                    f"Skipped queue to track {index} of {len(player.queue) + 1}"
                )

                if index - 1 != 0:
                    player.queue = player.queue[index - 1 :]

            else:
                logger.debug(
                    f"Jumped to track {index} of {len(player.queue)} in queue."
                )
                jump_track = player.queue.pop(index - 1)

                if not jump_track:
                    await itr.followup.send("Error! Track not found.")
                    return

                player.add(jump_track, index=0)

            next_track = player.queue[0]
            if isinstance(next_track, lavalink.DeferredAudioTrack):
                next_track = await next_track.load(self.bot.lavalink)
                try:
                    next_track = lavalink.decode_track(next_track)

                except Exception as e:
                    logger.error(e)

            if not next_track:
                await itr.followup.send(":warning: Error! Track not found.")
                return

            await player.skip()
            logger.debug("Skipping current track...")

            embed = EmbedHandler.Skip(itr, player.current, player)
            await itr.followup.send(embed=embed.construct())

            self.queuehandler.update_pages(player)

            return
