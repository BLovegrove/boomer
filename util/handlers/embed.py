import discord
import lavalink
from loguru import logger
from StringProgressBar import progressBar as ProgressBar

from util import cfg

__all__ = ["EmbedHandler"]


class EmbedHandler:

    class Track:
        def __init__(
            self,
            itr: discord.Interaction,
            track: lavalink.AudioTrack | lavalink.DeferredAudioTrack,
            player: lavalink.DefaultPlayer,
        ) -> None:
            # create core template
            self.sender: discord.Member = itr.user
            self.embed = discord.Embed(
                color=cfg.bot.accent_color,
                description=f"Song by: {track.author}",
            )

            # add sender details to author segment
            self.embed.set_author(
                name=f"Song requested by {self.sender.display_name}: ",
                url=track.uri,
                icon_url=self.sender.avatar.url,
            )

            # update thumbnail based on deferred status
            if isinstance(track, lavalink.AudioTrack):
                self.embed.set_thumbnail(
                    url=f"https://i.ytimg.com/vi/{track.identifier}/mqdefault.jpg"
                )

            else:
                self.embed.set_thumbnail(url="https://i.imgur.com/hpjK2ym.png")

            # update title based on idle status
            if not player.current or player.fetch("idle"):
                self.embed.title = (
                    f"{cfg.player.loading_emoji} Now playing: {track.title}"
                )

            else:
                self.embed.title = track.title
                self.embed.set_footer(text=f"Song is #{len(player.queue) + 1} in queue")

        def construct(self):
            return self.embed

    class Cleared(Track):
        def __init__(
            self,
            interaction: discord.Interaction,
            track: lavalink.AudioTrack | lavalink.DeferredAudioTrack,
            player: lavalink.DefaultPlayer,
            index: int,
        ) -> None:
            super().__init__(interaction, track, player)

            if not track:
                return

            self.embed.set_author(
                name=f"{self.sender.display_name} cleared a song from the queue:",
                url=self.embed.author.url,
                icon_url=self.embed.author.icon_url,
            )

            self.embed.set_footer(text=f"Song was #{index} in queue")

    class Skip(Track):
        def __init__(
            self,
            interaction: discord.Interaction,
            track: lavalink.AudioTrack | lavalink.DeferredAudioTrack,
            player: lavalink.DefaultPlayer,
        ) -> None:
            super().__init__(interaction, track, player)

            self.embed.set_author(
                name=f"Track(s) skipped by {self.sender.display_name}",
                url=self.embed.author.url,
                icon_url=self.embed.author.icon_url,
            )
            self.embed.title = f"Now playing: {track.title}"
            self.embed.set_footer(
                text=f"{max(0, len(player.queue) - 1)} track(s) left in queue."
            )

    class Progress(Track):
        def __init__(
            self,
            itr: discord.Interaction,
            player: lavalink.DefaultPlayer,
        ) -> None:
            super().__init__(itr, player.current, player)

            if not player.current:
                return

            # progress bar data
            self.total = player.current.duration
            self.current = int(player.position)
            self.progress = ProgressBar.splitBar(
                self.total,
                self.current,
                20,
            )

            self.embed.set_author(
                name=f"Info requested by: {self.sender.display_name}",
                url=self.embed.author.url,
                icon_url=self.embed.author.icon_url,
            )

            # self.timestamp_current = str(timedelta(milliseconds=self.current)).split(".")[0]
            # self.timestamp_total = str(timedelta(milliseconds=self.total)).split(".")[0]
            self.embed.set_footer(
                text=f"🎵 {lavalink.format_time(self.current)} {self.progress[0]} {lavalink.format_time(self.total)} 🎵",
            )

    class Playlist:
        def __init__(
            self,
            interaction: discord.Interaction,
            result: lavalink.LoadResult,
            player: lavalink.DefaultPlayer,
        ) -> None:
            if result.load_type != lavalink.LoadType.PLAYLIST:
                return

            self.sender: discord.Member = interaction.user
            self.tracks = result.tracks
            self.playlist = result.playlist_info
            self.player = player

            self.embed = discord.Embed(
                color=cfg.bot.accent_color,
                description=f":notepad_spiral: Playlist: {self.playlist.name}",
            )
            self.embed.set_author(
                name=f"Playlest queued by {self.sender.display_name}",
                icon_url=self.sender.display_avatar.url,
            )
            self.embed.set_thumbnail(
                url=f"https://i.ytimg.com/vi/{self.tracks[0].identifier}/mqdefault.jpg"
            )

            self.queue_length = len(player.queue)

            if player.is_playing or player.fetch("idle"):
                self.embed.title = f"Now playing: {self.tracks[0].title}"
                self.embed.set_footer(
                    text=f"Remaining songs are #1 to #{len(self.tracks) - 1} in queue."
                )

            else:
                self.embed.title = f"Added {self.tracks[0].title} and {len(self.tracks) - 1} more to queue."
                self.embed.set_footer(
                    text=f"Songs are #{(self.queue_length + 1 if self.queue_length > 0 else 1)} to #{len(self.player.queue) + len(self.tracks)} in queue."
                )

        def construct(self):
            return self.embed

    class List:
        def __init__(self, player: lavalink.DefaultPlayer, page: int) -> None:
            logger.debug(
                f"List embed page number requested: {page}. Total pages: {player.fetch('pages')}"
            )

            self.list_start = (page - 1) * 9
            self.list_end = (
                self.list_start + (9 - 1)
                if page < player.fetch("pages")
                else len(player.queue) - 1
            )

            self.track = player.current

            self.modifiers = (
                ""
                + (":repeat_one: " if player.loop == player.LOOP_SINGLE else "")
                + (":repeat: " if player.loop == player.LOOP_QUEUE else "")
                + (":twisted_rightwards_arrows: " if player.shuffle else "")
            )

            if self.modifiers == "":
                self.modifiers = "None."

            self.embed = discord.Embed(
                color=cfg.bot.accent_color,
                title=f"Now playing: ***{self.track.title}***",
                description=f"Page {page} of {player.fetch('pages')}. Modifiers: {self.modifiers}",
                url=self.track.uri,
            )
            self.embed.set_author(
                name=f"Current queue: Showing #{self.list_start + 1} to #{self.list_end + 1} of #{len(player.queue)} items in queue.",
                icon_url="https://i.imgur.com/dpVBIer.png",
            )
            self.embed.set_footer(text="<> for page +/-")

            if isinstance(self.track, lavalink.AudioTrack):
                self.embed.set_thumbnail(
                    url=f"https://i.ytimg.com/vi/{self.track.identifier}/mqdefault.jpg"
                )

            else:
                self.embed.set_thumbnail(url="https://i.imgur.com/hpjK2ym.png")

            for i in range(self.list_start, self.list_end + 1):
                track = player.queue[i]
                play_time = lavalink.format_time(track.duration)

                title = f"{i + 1}. *{track.title}*"
                title = title[:50] + "...*" if len(title) > 50 else title

                self.embed.add_field(name=title, value=f"{play_time}", inline=False)

        def construct(self):
            return self.embed

    class Favs:
        def __init__(self, title: str, favs: dict[str, str]) -> None:
            self.embed = discord.Embed(
                color=cfg.bot.accent_color,
                title=title,
                description="Simply click the buttons below to ready up that song and hit submit to add all ready songs to the queue!",
            )
            # self.embed.set_author(
            #     name="This is still a WIP. For now, this only prints a list of all your favourites. Sorry!"
            # )
            # self.embed.set_footer(text="Keep in mind you can only ready each song once!")
            for key, value in list(favs.items()):
                self.embed.add_field(
                    name=key, value=f"[{value}]({value})", inline=False
                )

        def construct(self):
            return self.embed
