import traceback

import discord
import lavalink

import config as cfg

from ..handlers.embeds import PlaylistEmbedBuilder, SkipEmbedBuilder, TrackEmbedBuilder
from ..handlers.presence import PresenceHandler
from ..handlers.queue import QueueHandler
from ..handlers.voice import VoiceHandler
from ..util import models


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

        elif tracks and result:
            embed = PlaylistEmbedBuilder(interaction, result, player).construct()

            for track in tracks:
                player.add(track)

        if player.fetch("idle"):
            player.store("idle", False)
            player.set_loop(player.LOOP_NONE)
            await player.set_volume(cfg.player.volume_default)
            await player.skip()

        elif not player.is_playing:
            await player.set_volume(cfg.player.volume_default)
            await player.play()

        await interaction.followup.send(embed=embed)

    async def play(self, inter: discord.Interaction, search: str):
        player: lavalink.DefaultPlayer = await self.voice_handler.ensure_voice(inter)

        if "https://" not in search:
            search = "ytsearch:" + search

        player.node: lavalink.Node = player.node
        result: lavalink.LoadResult = await player.node.get_tracks(f"{search}")

        try:
            match result.load_type:
                case lavalink.LoadType.LOAD_FAILED:
                    await inter.followup.send(
                        content="Failed to load track, please use a different URL or different search term."
                    )

                case lavalink.LoadType.NO_MATCHES:
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

        except Exception as e:
            stacktrace = traceback.extract_stack(e.__traceback__.tb_frame)
            return

        self.queue_handler.update_pages(player)

        return

    async def skip(
        self, inter: discord.Interaction, index: int, trim_queue: bool = True
    ):
        player = await self.voice_handler.ensure_voice(inter)

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
            return

        if index < 0:
            await inter.followup.send(
                ":warning: That index is too low! Queue starts at #1.", ephemeral=True
            )
            return

        elif index > len(player.queue):
            await inter.followup.send(
                f":warning: That index is too high! Queue only {len(player.queue)} items long.",
                ephemeral=True,
            )
            return

        else:
            if trim_queue:

                if index - 1 != 0:
                    player.queue = player.queue[index - 1 :]

            else:
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
                    pass

            if not next_track:
                await inter.followup.send(":warning: Error! Track not found.")
                return

            await player.skip()

            embed = SkipEmbedBuilder(inter, player.current, player)
            await inter.followup.send(embed=embed.construct())

            self.queue_handler.update_pages(player)

            return
