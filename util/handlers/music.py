import traceback

import discord
import lavalink
from loguru import logger

import util.config as cfg

from util.handlers.embeds import (
    PlaylistEmbedBuilder,
    SkipEmbedBuilder,
    TrackEmbedBuilder,
)
from util.handlers.presence import PresenceHandler
from util.handlers.queue import QueueHandler
from util.handlers.voice import VoiceHandler
from util import models


class MusicHandler:
    def __init__(self, bot: models.LavaBot) -> None:
        self.bot = bot
        self.voice_handler = VoiceHandler(self.bot)
        self.queue_handler = QueueHandler(self.bot, self.voice_handler)

    async def __add_track(
        self,
        interaction: discord.Interaction,
        player: lavalink.DefaultPlayer,
        track: lavalink.AudioTrack = None,
        tracks: list[lavalink.AudioTrack] = None,
        result: lavalink.LoadResult = None,
    ):
        embed = discord.Embed()

        if track:
            embed = TrackEmbedBuilder(interaction, track, player).construct()
            player.add(track)
            logger.info(f"Track added to queue: {track.title}")

        elif tracks and result:
            embed = PlaylistEmbedBuilder(interaction, result, player).construct()

            for track in tracks:
                player.add(track)

            logger.info(f"Playlist added to queue.")

        if player.fetch("idle"):
            player.store("idle", False)
            player.set_loop(player.LOOP_NONE)
            # await player.set_volume(cfg.player.volume_default)
            await player.skip()

        elif not player.is_playing:
            # await player.set_volume(cfg.player.volume_default)
            await player.play()

        await interaction.followup.send(embed=embed)

    async def play(self, inter: discord.Interaction, search: str):
        player: lavalink.DefaultPlayer = await self.voice_handler.ensure_voice(inter)
        if not player:
            return

        if "https://" not in search:
            search = "ytsearch:" + search

        logger.info(f"Attempting to play song... Query: {search}")

        result = await player.node.get_tracks(f"{search}")

        try:
            match result.load_type:
                case lavalink.LoadType.ERROR:
                    await inter.followup.send(
                        content="Failed to load track, please use a different URL or different search term."
                    )

                case lavalink.LoadType.EMPTY:
                    await inter.followup.send(
                        content="404 song not found! Try something else."
                    )

                case lavalink.LoadType.SEARCH | lavalink.LoadType.TRACK:
                    track = result.tracks[0]
                    await self.__add_track(inter, player, track)

                case lavalink.LoadType.PLAYLIST:
                    tracks = result.tracks
                    await self.__add_track(inter, player, None, tracks, result)

                case _:
                    await inter.followup.send(
                        content="Something unexpected happened. Contact your server owner or local bot dev(s) immediately and let them know the exact command you tried to run."
                    )
                    logger.warning(
                        f"Load type for play request defaulted. Query '{search}' result as follows:"
                    )
                    logger.warning(result)

        except Exception as e:
            stacktrace = traceback.extract_stack(e.__traceback__.tb_frame)
            logger.exception(
                f'Error while attempting to play track from "{stacktrace[-2].filename}", line {stacktrace[-2].lineno}'
            )
            return

        self.queue_handler.update_pages(player)

        return

    async def skip(
        self, inter: discord.Interaction, index: int, trim_queue: bool = True
    ):
        player = await self.voice_handler.ensure_voice(inter)

        logger.debug(f"Queue length: {len(player.queue)}, loop status: {player.loop}")
        if len(player.queue) == 0 and player.fetch("idle"):
            await inter.followup.send(
                ":notepad_spiral: End of queue - time for your daily dose of idle tunes!"
            )
            await player.skip()
            return

        if player.loop == player.LOOP_SINGLE:
            next_track = player.current

            if not next_track:
                await inter.followup.send(
                    f"Error! Track not found. Somethign went wrong with playback - try kicking {cfg.bot.name} from the VC and trying again."
                )
                return

            embed = SkipEmbedBuilder(inter, next_track, player, 0)
            await inter.followup.send(
                ":repeat_one: Repeat enabled - looping song.",
                embed=embed.construct(),
            )
            await player.seek(0)
            logger.info("Skipped song (repeat enabled).")
            return

        if index < 0:
            await inter.followup.send(
                ":warning: That index is too low! Queue starts at #1.", ephemeral=True
            )
            logger.warning(
                f"Skip failed. Index too low (expected: >=1. Recieved: {index})"
            )
            return

        elif index > len(player.queue):
            await inter.followup.send(
                f":warning: That index is too high! Queue only {len(player.queue)} items long.",
                ephemeral=True,
            )
            logger.warning(
                f"Skip failed. Index too high (expected: <={len(player.queue)}. Recieved: {index})"
            )
            return

        else:
            if trim_queue:
                logger.info(
                    f"Skipped queue to track {index} of {len(player.queue) + 1}"
                )

                if index - 1 != 0:
                    player.queue = player.queue[index - 1 :]

            else:
                logger.info(f"Jumped to track {index} of {len(player.queue)} in queue.")
                jump_track = player.queue.pop(index - 1)

                if not jump_track:
                    await inter.followup.send("Error! Track not found.")
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
                await inter.followup.send(":warning: Error! Track not found.")
                return

            await player.skip()
            logger.info("Skipping current track...")

            embed = SkipEmbedBuilder(inter, player.current, player)
            await inter.followup.send(embed=embed.construct())

            self.queue_handler.update_pages(player)

            return
