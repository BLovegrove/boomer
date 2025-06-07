import json
import os
from typing import Union
import discord
import lavalink
from loguru import logger
from StringProgressBar import progressBar as ProgressBar

from util import cfg, models

__all__ = ["EmbedHandler"]


class EmbedHandler:

    @staticmethod
    def get_artwork_url(track: Union[lavalink.AudioTrack, lavalink.DeferredAudioTrack]):
        if track.artwork_url and isinstance(track, lavalink.AudioTrack):
            return track.artwork_url
        else:
            return cfg.image.unknown

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
            self.embed.set_thumbnail(url=EmbedHandler.get_artwork_url(track))

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
            itr: discord.Interaction,
            track: lavalink.AudioTrack | lavalink.DeferredAudioTrack,
            player: lavalink.DefaultPlayer,
            index: int,
        ) -> None:
            super().__init__(itr, track, player)

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
            itr: discord.Interaction,
            track: lavalink.AudioTrack | lavalink.DeferredAudioTrack,
            player: lavalink.DefaultPlayer,
        ) -> None:
            super().__init__(itr, track, player)

            self.embed.set_author(
                name=f"Track(s) skipped by {self.sender.display_name}",
                url=self.embed.author.url,
                icon_url=self.embed.author.icon_url,
            )
            self.embed.title = f"Now playing: {track.title}"
            self.embed.set_footer(text=f"{len(player.queue)} track(s) left in queue.")

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
            itr: discord.Interaction,
            tracks: list[Union[lavalink.AudioTrack, lavalink.DeferredAudioTrack]],
            name: str,
            player: lavalink.DefaultPlayer,
        ) -> None:

            self.sender: discord.Member = itr.user
            self.tracks = tracks
            self.player = player

            self.embed = discord.Embed(
                color=cfg.bot.accent_color,
                description=f":notepad_spiral: Playlist: {name}",
            )
            self.embed.set_author(
                name=f"Playlest queued by {self.sender.display_name}",
                icon_url=self.sender.display_avatar.url,
            )

            self.embed.set_thumbnail(url=EmbedHandler.get_artwork_url(tracks[0]))

            self.queue_length = len(self.player.queue)

            if not self.player.is_playing or player.fetch("idle"):
                self.embed.title = f"Now playing: {self.tracks[0].title}"
                self.embed.set_footer(
                    text=f"Remaining songs are #1 to #{len(self.tracks) - 1} in queue."
                )

            else:
                self.embed.title = f"Added {self.tracks[0].title} and {len(self.tracks) - 1} more to queue."
                self.embed.set_footer(
                    text=f"Songs are #{(self.queue_length + 1 if self.queue_length > 0 else 1)} to #{self.queue_length + len(self.tracks)} in queue."
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
                name=f"Current queue: Showing #{self.list_start + 1 if len(player.queue) > 0 else 0} to #{self.list_end + 1} of #{len(player.queue)} items in queue.",
                icon_url=cfg.image.boombox,
            )
            self.embed.set_footer(text="<> for page +/-")

            self.embed.set_thumbnail(url=EmbedHandler.get_artwork_url(self.track))

            for i in range(self.list_start, self.list_end + 1):
                track = player.queue[i]
                play_time = lavalink.format_time(track.duration)

                title = f"{i + 1}. *{track.title}*"
                title = title[:50] + "...*" if len(title) > 50 else title

                self.embed.add_field(name=title, value=f"{play_time}", inline=False)

        def construct(self):
            return self.embed

    class Favs:
        def __init__(self, bot: models.LavaBot, favs: dict[str, any]) -> None:
            owner = favs["owner_id"]

            try:
                if discord.utils.get(
                    bot.get_guild(cfg.bot.guild_id).members, id=int(owner)
                ):
                    owner = (
                        discord.utils.get(
                            bot.get_guild(cfg.bot.guild_id).members, id=int(owner)
                        ).display_name
                        + " - "
                    )

                elif discord.utils.get(
                    bot.get_guild(cfg.bot.guild_id).roles, id=int(owner)
                ):
                    owner = (
                        discord.utils.get(
                            bot.get_guild(cfg.bot.guild_id).roles, id=int(owner)
                        ).name
                        + " - "
                    )

                else:
                    owner = "Unknown - "

            except:
                owner = "Global Default - "

            favs_list: dict[str, str] = json.loads(favs["entries"])
            desc = []
            for key, value in list(favs_list.items()):
                desc.append(f"- **[{key}]({value})**")

            self.embed = discord.Embed(
                color=cfg.bot.accent_color,
                title=owner + favs["name"],
                description="\n".join(desc),
            )
            # self.embed.set_author(
            #     name="This is still a WIP. For now, this only prints a list of all your favourites. Sorry!"
            # )
            # self.embed.set_footer(text="Keep in mind you can only ready each song once!")
            # for key, value in list(favs.items()):
            #     self.embed.add_field(
            #         name=key,
            #         value=f"[{value}]({value})",
            #         inline=False,
            #     )

        def construct(self):
            return self.embed
