import asyncio
import logging
import re
import __main__
import time
import math
from typing import Dict, List
from datetime import datetime
import textwrap
from discord import emoji, message, permissions, player
from discord.ext.commands.converter import IDConverter
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import discord_slash
from discord_slash.client import SlashCommand
from discord_slash.context import ComponentContext
from discord_slash.model import SlashCommandPermissionType
from discord_slash.utils import manage_commands
from discord_slash.utils.manage_commands import create_option, create_permission
from discord_slash.utils import manage_components
from discord_slash.model import ButtonStyle
from lavalink.models import AudioTrack, DefaultPlayer
from lavalink.utils import decode_track
from .. import config
from .. import util
import discord
import lavalink
from discord.ext import commands
from discord_slash import SlashContext, cog_ext
import json

standard_rx = re.compile(r'https?://(?:www\.)?.+')
spotify_rx = re.compile
cfg = config.load_config()


async def timestamp():
    print(f"time: {datetime.now()}")

# ------------------------------- ANCHOR CLASS ------------------------------- #

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot: discord.Client = bot
        self.activity_idle = discord.Streaming(name="nothing.", url="https://tinyurl.com/lamzterms")
            
        bot.lavalink = lavalink.Client(cfg['bot']['id'])
        # Host, Port, Password, Region, Name
        cfg_lava = cfg['lavalink']
        bot.lavalink.add_node(
            host=cfg_lava['ip'], 
            port=cfg_lava['port'], 
            password=cfg_lava['pwd'], 
            region=cfg_lava['region'], 
            reconnect_attempts=-1
        )
        bot.add_listener(bot.lavalink.voice_update_handler,'on_socket_response')

        client_credentials_manager = SpotifyClientCredentials(
            client_id=cfg['spotify']['id'], 
            client_secret=cfg['spotify']['secret']
        )
        self.spotify = spotipy.Spotify(client_credentials_manager = client_credentials_manager)

        lavalink.add_event_hook(self.hooks)

    # ---------------------------------------------------------------------------- #
    #                         SECTION[id=callbacks] -EVENTS                        #
    # ---------------------------------------------------------------------------- #

    # ---------------------------- ANCHOR PLAYER HOOKS --------------------------- #
    # Runs whenever an event is raised by the player. Run things like EndQueue and 
    # EndTrack etc. 

    async def hooks(self, event):

        # if isinstance(event, lavalink.events.TrackStartEvent):
        #     print(f"Track that is playing:\n{event.track.title}")

        # if isinstance(event, lavalink.events.TrackEndEvent):

        #     player = event.player
        #     interrupt = player.fetch('interrupt_time')

        #     if interrupt:
        #         player.store('interrupt_time', None)
        #         print('cleared interrupt flag')
        #         player.add(cfg['bot']['id'], player.fetch('interrupt_track'), 0)
        #         print('added song to queue')
        #         await player.play(start_time=20000)
        #         print('playing song')
        #         print(f"Track that should be playing:\n{player.fetch('interrupt_track').title}")

        if isinstance(event, lavalink.events.TrackEndEvent):

            player = event.player
            repeat_track = player.fetch('repeat_one')

            if repeat_track:
                player.add(requester=cfg['bot']['id'], track=repeat_track, index=0)

        if isinstance(event, lavalink.events.QueueEndEvent):
            # Play idle music when no tracks are left in queue

            guild_id = int(event.player.guild_id)
            guild = self.bot.get_guild(guild_id)

            player = event.player

            if player.fetch('repeat_one'):
                return

            player.store('volume_guild', player.volume)
            await player.set_volume(cfg['music']['volume_idle'])

            results = await player.node.get_tracks(cfg['music']['idle_track'])

            if not results or not results['tracks'] or results['loadType'] != 'TRACK_LOADED':
                player.queue.clear()
                await player.stop()
                await guild.change_voice_state(channel=None)
                return print('Nothing found for idle music! look for a new video.')

            player.store('idle', True)
            track = results['tracks'][0]
            player.add(requester=cfg['bot']['id'], track=track)
            if not player.is_playing:
                await player.play()
                await self.update_status(player)

    # ---------------------------- ANCHOR LIST BUTTONS --------------------------- #
    # Callbacks for list button slash commands

    # Common func for getting page numer x of y in [x,y] format from a list embed
    def get_list_page(self, btx: ComponentContext) -> List[int]:
        page_string = btx.origin_message.embeds[0].description
        page_numbers = []

        for part in page_string.split():
            part = part.strip(".,:")
            if part.isdigit():
                page_numbers.append(int(part))

        return page_numbers

    # Go backward in /list to the previous page
    @cog_ext.cog_component()
    async def list_page_prev(self, btx: ComponentContext):

        player = self.fetch_player(btx)

        try:
            page = self.get_list_page(btx)[0]
        except IndexError:
            await btx.send(f"Something went wrong while extracting the page numbers from the embeds description. Contact <@{cfg['owner_id']}>.")
            return

        if page <= 1:
            embed = self.embed_list(player, page)
            await btx.edit_origin(embeds=[embed])
            return

        embed = self.embed_list(player, page - 1)
        await btx.edit_origin(embeds=[embed])

    # Go forward in /list to the next page
    @cog_ext.cog_component()
    async def list_page_next(self, btx: ComponentContext):

        player = self.fetch_player(btx)
        if not player:
            return

        try:
            page_data = self.get_list_page(btx)
            page = page_data[0]
            pages = page_data[1]
        except IndexError:
            await btx.send(f"Something went wrong while extracting the page numbers from the embeds description. Contact <@{cfg['owner_id']}>.")
            return

        if page >= pages:
            embed = self.embed_list(player, page)
            await btx.edit_origin(embeds=[embed])
            return

        embed = self.embed_list(player, page + 1)
        await btx.edit_origin(embeds=[embed])

    # --------------------------------- !SECTION --------------------------------- #

    # ---------------------------------------------------------------------------- #
    #                       SECTION[id=helpers] -HELPERS                           #
    # ---------------------------------------------------------------------------- #

    # ---------------------------- ANCHOR UPDATE STATUS -------------------------- #
    # Updates boomers status message with whatever song is currently playing

    async def update_status(self, player: DefaultPlayer):

        if player.fetch("repeat_one"):
            suffix = " (on repeat)"
        elif player.shuffle:
            suffix = " (shuffle)"
        else:
            suffix = ""

        if player.current:
            activity = discord.Game(player.current.title + suffix)
            status = discord.Status.online

        else:
            activity = discord.Game("nothing.")
            status = discord.Status.idle
            
        await self.bot.change_presence(activity=activity, status=status)

    # ---------------------------- ANCHOR FETCHPLAYER ---------------------------- #
    # Returns the bots player if one exists otherwise sets up the default one and
    # returns that

    def fetch_player(self, ctx: SlashContext) -> lavalink.DefaultPlayer:
        # Create returns a player if one exists, otherwise creates.
        return self.bot.lavalink.player_manager.create(
            ctx.guild.id, endpoint=str(ctx.guild.region)
        )

    # ---------------------------- ANCHOR ENSUREVOICE ---------------------------- #
    # Makes sure boomer joins a voice channel if commands that need it are queued (
    # i.e. anything that plays or queues a song). Otherwise makes sure you're in the 
    # the same voice channel as the bot to run things.

    async def ensure_voice(self, ctx: SlashContext) -> lavalink.DefaultPlayer or None:
        # This check ensures that the bot and command author are in the same voicechannel.

        player = self.fetch_player(ctx)

        # These are commands that require the bot to join a voicechannel.
        should_connect = ctx.command in ('play','zplay','ok','lofi','test','best')

        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send('Join a voicechannel first.')
            return

        if not player.is_connected:
            if not should_connect:
                await ctx.send('Not connected.')
                return

            player.store('pages', 0)
            player.store('channel', ctx.channel.id)
            player.store('voice', ctx.author.voice.channel)
            await ctx.guild.change_voice_state(channel=ctx.author.voice.channel)

            return player
        else:
            if int(player.channel_id) != ctx.author.voice.channel.id:
                await ctx.send(f"You need to be in <#{player.channel_id}> to do that.")
                return

            return player

    def get_playing(self, player: lavalink.DefaultPlayer) -> lavalink.AudioTrack:
        if player.current:
            track = player.current
        elif self.looping:
            track = player.fetch('repeat_one')
        else:
            track = player.queue[0]
        return track


    # ---------------------------- ANCHOR UPDATE PAGES --------------------------- #
    # Updates the number of pages defined in the config file as queue_page_len 

    def update_pages(self, player: lavalink.DefaultPlayer):
        player.store('pages', math.ceil(
            len(player.queue) / cfg['music']['queue_page_len']))

    # --------------------------- ANCHOR SPOTIFY PLIST --------------------------- #
    # Gets spotify playlist info and returns a pandas dataframe of all the songs in
    # the playlist

    def sp_get_playlist(self, playlist_id: str) -> dict:
        playlist_features = ['artist', 'track_name', 'album']
        playlist_df = pd.DataFrame(columns=playlist_features)

        # playlist = self.spotify.user_playlist_tracks(creator, playlist_id)['items']
        playlist = self.spotify.playlist_tracks(playlist_id)['items']
        playlist_title = self.spotify.playlist(
            playlist_id, 
            fields="name"
        )['name']

        for track in playlist:
            playlist_features = {}

            playlist_features["artist"] = track["track"]["album"]["artists"][0]["name"]
            playlist_features["album"] = track["track"]["album"]["name"]
            playlist_features["track_name"] = track["track"]["name"]

            track_df = pd.DataFrame(playlist_features, index=[0])
            playlist_df = pd.concat([playlist_df, track_df], ignore_index=True)

        playlist = {'title': playlist_title, 'data': playlist_df}

        return playlist

    # -------------------------------- ANCHOR PLAY ------------------------------- #
    # Core method for this class. Takes query and uses lavalink to grab / enqueue results.
    # Plays frist result directly if nothign else in in the queue and kills idle state / resets
    # volume if needed.

    async def play(self, ctx: SlashContext, query: str):
        player = await self.ensure_voice(ctx)
        if not player:
            return
        else:
            logging.info(f"[{ctx.author.name}" + (f"#{ctx.author.discriminator}" if ctx.author.discriminator else "#0000") + f"] Attempting to play song... Query: {query}")

        await ctx.defer()
        results = None

        if not standard_rx.match(query):
            query = f"ytsearch:{query}"
            results = await player.node.get_tracks(query)

        else:
            if "open.spotify.com" in query:
                if "playlist" in query:
                    playlist_id = query.split("/")[-1].split("?")[0]
                    playlist = self.sp_get_playlist(playlist_id)
                    tracks = []

                    embed = discord.Embed(color=discord.Color.blurple())
                    embed.set_author(
                        name=f"Loading spotify playlist: {playlist['title']}",
                        url="https://tinyurl.com/boomermusic",
                        icon_url="https://i.imgur.com/dpVBIer.png"
                    )
                    embed.description = util.progress_bar(
                        0, len(playlist['data']))
                    embed.set_footer(
                        text="Please note: This can take a long time for playlists larger than 20 songs"
                    )

                    logging.info("Trying to get spotify playlist. Better get some popcorn while you wait.")
                    loading_msg = await ctx.send(embed=embed)
                    await loading_msg.edit(embeds=[embed])

                    for index, row in playlist['data'].iterrows():
                        track = await player.node.get_tracks(f"ytsearch:{row['track_name']} by {row['artist']}")
                        try:
                            track = track['tracks'][0]
                        except:
                            logging.warn("Play failed! Track not found.")

                        tracks.append(track)
                        if len(tracks) % 1 == 0:
                            embed.description = util.progress_bar(
                                len(tracks), 
                                len(playlist['data'])
                            )
                            await loading_msg.edit(embeds=[embed])

                    embed.description = util.progress_bar(
                        len(tracks), 
                        len(playlist['data'])
                    )
                    await loading_msg.edit(content="Playlist loaded! :tada:")
                    logging.info("Finished gathering spotify tracks. Finally.")

                    results = {
                        'playlistInfo': {
                            'selectedTrack': 0,
                            'name': playlist['title']
                        },
                        'loadType': 'PLAYLIST_LOADED',
                        'tracks': tracks
                    }

                # elif "track" in query:
                #     playlist_id = query.split("/")[-1].split("?")[0]
                    # playlist = self.sp_get
                    # query =
            else:
                results = await player.node.get_tracks(query)
        
        if not results or not results['tracks']:
            logging.warn("Query failed. No song(s) found.")
            return await ctx.send(':x: Nothing found!')

        embed = discord.Embed(color=discord.Color.blurple())

        if results['loadType'] == 'PLAYLIST_LOADED':
            # Grab playlist info
            tracks = results['tracks']
            info = results['playlistInfo']

            # Populate embed
            embed.set_author(
                name=f"Playlist queued by {ctx.author.display_name}: ",
                url="https://tinyurl.com/boomermusic",
                icon_url=ctx.author.avatar_url
            )
            embed.description = f":notepad_spiral: Playlist: {info['name']}"
            embed.url = tracks[0]['info']['uri']
            embed.set_thumbnail(
                url=f"https://i.ytimg.com/vi/{tracks[0]['info']['identifier']}/mqdefault.jpg"
            )
            # Change message if this is the first item queued vs not
            if not player.is_playing and len(player.queue) == 0 or player.fetch('idle'):
                embed.title = f"Now playing: {tracks[0]['info']['title']}"
                embed.set_footer(
                    text=f"Remaining songs are #1 to #{len(tracks) - 1} in queue."
                )
            else:
                embed.title = f"Added {tracks[0]['info']['title']} and {len(tracks) - 1} more to queue"
                embed.set_footer(
                    text=f"Songs are #{len(player.queue)} to #{len(player.queue) + len(tracks)} in queue."
                )

            # Add all tracks to the queue
            for track in tracks:
                player.add(requester=ctx.author.id, track=track)

            logging.info(f"Found playlist. Playing from list: {results['playlistInfo']}.")

        else:
            # Grab track info
            track = results['tracks'][0]
            info = track["info"]

            # Populate embed
            embed.set_author(
                name=f"Song queued by {ctx.author.display_name}: ",
                url=info["uri"],
                icon_url=ctx.author.avatar_url
            )
            embed.description = f"Song by: {info['author']}"
            embed.set_thumbnail(
                url=f"https://i.ytimg.com/vi/{info['identifier']}/mqdefault.jpg"
            )

            # Change messgae if this is the first item queued vs not
            if not player.is_playing and len(player.queue) == 0 or player.fetch('idle'):
                embed.title = f"Now playing: {info['title']}"
            else:
                embed.title = info['title']
                embed.set_footer(
                    text=f"Song is #{len(player.queue) + 1} in queue."
                )

            # Add song to playlist
            player.add(requester=ctx.author.id, track=track)
            logging.info(f"Found song. Adding track to queue: {info}.")

        await ctx.send('',embed=embed)

        # Start playing if no song is in queue
        if player.fetch('idle'):
            player.store('idle', False)
            await player.play()
            await player.set_volume(player.fetch('volume_guild'))

        elif not player.is_playing:
            await player.set_volume(cfg['music']['volume_default'])
            await player.play()

        await self.update_status(player)
        self.update_pages(player)


    # ----------------------------- ANCHOR EMBED LIST ---------------------------- #
    # Used by the list command to put a queue summary together

    def embed_list(self, player: lavalink.DefaultPlayer, page: int) -> discord.Embed:
        queue_start = (page - 1) * cfg['music']['queue_page_len']
        queue_end = queue_start + ( cfg['music']['queue_page_len'] - 1) if page < player.fetch('pages') else len(player.queue) - 1
        if queue_end == 0:
            queue_end += 1

        track = self.get_playing(player)

        modifiers = ""
        if player.fetch('repeat_one'):
            modifiers += ":repeat_one: "

        if player.repeat:
            modifiers += ":repeat: "

        if player.shuffle:
            modifiers += ":twisted_rightwards_arrows: "

        modifiers = "None" if modifiers == "" else modifiers

        embed = discord.Embed(
            color=discord.Color.blurple(),
            title=f"Now playing: ***{track.title}***",
            description=f"Page {page} of {player.fetch('pages')}. Modifiers: {modifiers}",
            url=track.uri
        )
        embed.set_author(
            name=f"Current playlist: Showing #{queue_start + 1} to #{queue_end + 1} of {len(player.queue)} items in queue.",
            url="https://tinyurl.com/boomermusic",
            icon_url="https://i.imgur.com/dpVBIer.png"
        )
        embed.set_thumbnail(
            url=f"https://i.ytimg.com/vi/{track.identifier}/mqdefault.jpg"
        )
        for i in range(queue_start, queue_end + 1):
            track: lavalink.AudioTrack = player.queue[i]
            play_time = lavalink.format_time(track.duration)

            # Strip 00: hour from a video if its less than an hour long
            if play_time.startswith("00:"):
                play_time = play_time[3:]

            embed.add_field(
                name=textwrap.shorten(f"{i + 1}. *{track.title}*", width=cfg['music']['list_char_len']),
                value=f"{play_time}",
                inline=False
            )

        embed.set_footer(
            text=f"<> for page +/-, dropdown to select track, ❌/⏭️ to clear/skip to track."
        )

        return embed

    # ---------------------------- ANCHOR EMBED TRACK ---------------------------- #

    async def embed_track(self, ctx: SlashContext, track: lavalink.AudioTrack, action: str, queue_len: int, footer: str="", author: str="") -> discord.Embed:
        """Constructs and returns and embed for a single track. 
        Action gets prepended to author title (action by user. Now playing: ). 
        Author overrides entire author name section ('now playing' by default).

        Args:
            ctx (SlashContext): Discord context for the command
            track (AudioTrack): Lavalink track to grab information from
            action (str): The action string. See desc. for example
            queue_len (int): Length of player queue at time of embed request
            footer (str): Optional arg for footer segment (blank by default)
            author (str): Optional override for author segment of the embed (the 'now playing' segment by default)

        Returns:
            discord.Embed: Embed with track info filled in
        """

        # Construct feedback embed
        embed = discord.Embed(
            color=discord.Color.blurple(),
            title=track.title,
            description=f"Song by: {track.author}",
        )

        if author == "":
            author_name = f"{action} by {ctx.author.display_name}. Now playing: "
        else:
            author_name = author

        embed.set_author(
            name=author_name,
            url=track.uri,
            icon_url=ctx.author.avatar_url
        )

        embed.set_thumbnail(
            url=f"https://i.ytimg.com/vi/{track.identifier}/mqdefault.jpg"
        )

        if footer == "":
            embed.set_footer(
                text=f"Songs remaining in queue: {queue_len}"
            )
        else:
            embed.set_footer(
                text=footer
            )

        return embed

    # -------------------------------- ANCHOR SKIP ------------------------------- #
    # Skips either the next song in queue or if specified skips to a specific index and
    # resumes the normal queue afterwards. trim_queue overrides that and clears queue up
    # to the requested index.

    async def skip(self, ctx, player: DefaultPlayer, index: int=None, trim_queue=True):
        embed_action = "Track skipped"
        logging.info(f"[{ctx.author.name}" + (f"#{ctx.author.discriminator}" if ctx.author.discriminator else "#0000") + f"] Skipping track...")

        if len(player.queue) > 0 or player.fetch('repeat_one'):
            # Get next track in playlist info

            if player.fetch('repeat_one'):
                next_track = player.fetch('repeat_one')
                queue_len = len(player.queue)
                embed = await self.embed_track(
                    ctx,
                    track=next_track,
                    action=embed_action,
                    queue_len=queue_len
                )

                await ctx.send(":repeat_one: Repeat enabled - repeating song.", embed=embed)
                await player.seek(0)
                logging.info(f"Skipped (Repeating song).")

            elif player.shuffle:
                await player.skip()
                next_track = player.current
                embed = await self.embed_track(
                    ctx,
                    track=next_track,
                    action=embed_action,
                    queue_len=len(player.queue)
                )
                await ctx.send(embed=embed)

            else:
                if index:
                    index = index - 1 # Revert index+=1 used for user readability
                    if index <= 0:
                        await ctx.send(":warning: That index is too low! Queue starts at #1.", hidden=True)
                        logging.warn(f"Skip failed. Index too low (Expected: >=1. Recieved: {index})")
                        return

                    elif index > len(player.queue):
                        await ctx.send(f":warning: That index is too high! Queue only {len(player.queue)} items long.", hidden=True)
                        logging.warn(f"Skip failed. Index too high (Expected: <={len(player.queue)}. Recieved: {index}")
                        return

                    else:
                        if trim_queue:
                            del player.queue[:index]
                            next_track = player.queue[0]
                            logging.info(f"Skipped queue to track {index} of {len(player.queue)}.")
                        else:
                            next_track = player.queue.pop(index)
                            player.queue.insert(0, next_track)
                            logging.info(f"Jumped to track {index} of {len(player.queue)} in queue.")


                else:
                    next_track = player.queue[0]
                    logging.info(f"Skipped current track.")

                embed = await self.embed_track(
                    ctx,
                    track=next_track,
                    action=embed_action,
                    queue_len=len(player.queue)
                )
                await ctx.send(embed=embed)
                await player.skip()
        else:
            await ctx.send(":notepad_spiral: End of queue - time for your daily dose of idle tunes.")
            await player.skip()

        await self.update_status(player)
        self.update_pages(player)

    # ------------------------------- ANCHOR CLEAR ------------------------------- #
    # Clears either the entire queue if no index is given or a single specific item
    # from the queue.

    async def clear(self, ctx: SlashContext, index: int=0):

        player = await self.ensure_voice(ctx)
        if not player:
            return

        if index == 0:
            player.queue = []
            player.store("pages", 0)
            await ctx.send(":boom: Queue cleared!")
            logging.info(f"[{ctx.author.name}" + (f"#{ctx.author.discriminator}" if ctx.author.discriminator else "#0000") + f"] Cleared queue.")
        else:
            cleared = player.queue.pop(index)
            embed = await self.embed_track(
                ctx=ctx, 
                track=cleared, 
                action="", 
                queue_len=len(player.queue), 
                author=f"{ctx.author.display_name} cleared a song from queue:"
            )
            self.update_pages(player)
            await ctx.send(embed=embed)

            logging.info(f"[{ctx.author.name}" + (f"#{ctx.author.discriminator}" if ctx.author.discriminator else "#0000") + f"] Cleared item from queue.")


    # --------------------------------- !SECTION --------------------------------- #

    # ---------------------------------------------------------------------------- #
    #                       SECTION[id=shortcuts] -SHORTCUTS                       #
    # ---------------------------------------------------------------------------- #

    # ------------------------------ ANCHOR OKBOOMER ----------------------------- #
    # Also manually calls the idle state hook for EndQueue

    @cog_ext.cog_subcommand(
        base="ok",
        name="boomer",
        description="Summons Boomer into a voice channel without playing anything",
        guild_ids=cfg['guild_ids']
    )
    async def okboomer(self, ctx: SlashContext):
        player = await self.ensure_voice(ctx)
        if not player:
            return
        else:
            logging.info(f"[{ctx.author.name}" + (f"#{ctx.author.discriminator}" if ctx.author.discriminator else "#0000") + f"] Summoning boomer...")

        await ctx.defer()

        if player.is_playing:
            await ctx.send(f"I'm already in <#{player.fetch('voice').id}> zoomer.")
            logging.warn("Summoning failed. You shall not pass (already in call).")
        else:
            await ctx.send(f"Joined <#{player.fetch('voice').id}>")
            await player.set_volume(10)
            await self.hooks(lavalink.QueueEndEvent(player))
            logging.info(f"Boomer joined #{player.fetch('voice').name}")

    # ----------------------------- ANCHOR LOFI RADIO ---------------------------- #
    # Simple shortcut for lofi beats because lavalink doesnt like searching for 
    # livestreams for some reason

    @cog_ext.cog_subcommand(
        base="lofi",
        name="radio",
        description="Plays the Lofi Hip Hop radio livestream.",
        guild_ids=cfg['guild_ids']
    )
    async def lofi_radio(self, ctx: SlashContext):
        player = await self.ensure_voice(ctx)
        if not player:
            return
        else:
            logging.info(f"[{ctx.author.name}" + (f"#{ctx.author.discriminator}" if ctx.author.discriminator else "#0000") + f"] Playing lofi radio...")

        query = "https://www.youtube.com/watch?v=5qap5aO4i9A"
        await self.play(ctx, query)

    # ----------------------------- ANCHOR TEST LIST ----------------------------- #
    # Queues up my default test playlist on youtube. Good for testing list function
    # and others.

    # @cog_ext.cog_subcommand(
    #     base="test",
    #     name="list",
    #     description="Queue up test playlist from youtube containing a few pages of items.",
    #     guild_ids=cfg['guild_ids']
    # )
    # async def test_list(self, ctx: SlashContext):
    #     player = await self.ensure_voice(ctx)
    #     if not player:
    #         return

    #     query = "https://www.youtube.com/watch?v=1hUvUWY0TgA&list=PLe6BSc2t2vrfW4BY1D0JZD2wMQURH9bqk"
    #     await self.play(ctx, query)

    # ------------------------------- ANCHOR PIRATE ------------------------------ #
    # Do you even need to ask?

    # @cog_ext.cog_subcommand(
    #     base="best",
    #     name="pirate",
    #     description="DUH-DUH-DUH DAH, DUH-DUH-DUH DAH, DUH-DUH-DUH DAH DUH-DUH-DUH-DUH",
    #     guild_ids=cfg['guild_ids']
    # )
    # async def best_pirate(self, ctx: SlashContext):
    #     player = await self.ensure_voice(ctx)
    #     if not player:
    #         return

    #     track_time = player.position
    #     track = player.current

    #     results = await player.node.get_tracks("https://www.youtube.com/watch?v=5GHbtOx8-cw")
    #     # player.add(ctx.author.id, player.current, 0)
    #     player.add(ctx.author.id, results['tracks'][0], 0)

    #     await player.play(start_time=1000)
    #     await ctx.send("So it would seem...")

    #     player.store('interrupt_time', track_time)
    #     player.store('interrupt_track', track)

    # --------------------------------- !SECTION --------------------------------- #

    # ---------------------------------------------------------------------------- #
    #                        SECTION[id=commands] -COMMANDS                        #
    # ---------------------------------------------------------------------------- #

    # -------------------------------- ANCHOR PLAY ------------------------------- #
    # Calls self.play and passes along song request / message context

    @cog_ext.cog_slash(
        name="play",
        description="Plays a song from given query / url.",
        guild_ids=cfg['guild_ids'],
        options=[
            create_option(
                name="song",
                description="Searches for a song on YouTube. Plays URL directly if given",
                option_type=str,
                required=True
            )
        ]
    )
    async def play_command(self, ctx: SlashContext, song: str):
        await self.play(ctx, song)

    # ------------------------------- ANCHOR PAUSE ------------------------------- #
    # pauses the current track. resumed with /resume

    @cog_ext.cog_slash(
        name="pause",
        description="Pauses the currently playing song. Resume with /resume.",
        guild_ids=cfg['guild_ids']
    )
    async def pause(self, ctx: SlashContext):
        player = await self.ensure_voice(ctx)
        if not player:
            return
        else:
            logging.info(f"[{ctx.author.name}" + (f"#{ctx.author.discriminator}" if ctx.author.discriminator else "#0000") + f"] Paused track.")
        
        await player.set_pause(True)
        await ctx.send(":pause_button: Paused track.")

    # ------------------------------- ANCHOR RESUME ------------------------------ #
    # resumes the current track. paused with /pause

    @cog_ext.cog_slash(
        name="resume",
        description="Resumes the currently playing song. Pause with /pause.",
        guild_ids=cfg['guild_ids']
    )
    async def resume(self, ctx: SlashContext):
        player = await self.ensure_voice(ctx)
        if not player:
            return
        else:
            logging.info(f"[{ctx.author.name}" + (f"#{ctx.author.discriminator}" if ctx.author.discriminator else "#0000") + f"] Resumed track.")
        
        await player.set_pause(False)
        await ctx.send(":arrow_forward: Resumed track.")

    # ------------------------------- ANCHOR LEAVE ------------------------------- #
    # Leave voice chat if in one. Also resets the queue and clears any modifiers.

    @cog_ext.cog_slash(
        name="leave",
        description="Disconnects Boomer from voice and clears the queue",
        guild_ids=cfg['guild_ids']
    )
    async def leave(self, ctx: SlashContext):
        player = await self.ensure_voice(ctx)
        if not player:
            return
        else:
            logging.info(f"[{ctx.author.name}" + (f"#{ctx.author.discriminator}" if ctx.author.discriminator else "#0000") + f"] Leaving channel... Cleared queue. Modifiers disabled. Volume reset to default.")

        player.queue.clear()
        await player.stop()
        await ctx.guild.change_voice_state(channel=None)
        player.store('repeat_one', None)
        player.set_repeat(False)
        player.set_shuffle(False)
        await player.set_volume(cfg['music']['volume_default'])
        await ctx.send(f":wave: Leaving <#{player.fetch('voice').id}> and clearing queue.")
        await self.update_status(player)

    # ------------------------------- ANCHOR VOLUME ------------------------------ #
    # Print volume, or ncrease / decrease volume. Capped at 0-50 (displayed as 0-100)
    # for normal users and 0-1000 for the server owner.

    @cog_ext.cog_slash(
        name="volume",
        description="See Boomer's volume level. Add level to change it.",
        guild_ids=cfg['guild_ids'],
        options=[
            create_option(
                name="level",
                description="Volume level from 0% to 100%",
                option_type=int,
                required=False
            )
        ]
    )
    async def volume(self, ctx: SlashContext, level: int = None):
        player = await self.ensure_voice(ctx)
        volume = level # Make dealing with volume more sensible
        if not player:
            return

        if volume:
            if ctx.author.id != cfg['owner_id']:
                volume = util.clamp(volume, 0, 100)
                await player.set_volume(math.ceil(volume / 2))
            else:
                await player.set_volume(volume)

            logging.info(f"[{ctx.author.name}" + (f"#{ctx.author.discriminator}" if ctx.author.discriminator else "#0000") + f"] Set volume to {volume}.")

        else:
            volume = player.volume

        if volume <= 33:
            volume_emote = ":speaker:"
        elif volume > 33 and volume <= 66:
            volume_emote = ":sound:"
        else:
            volume_emote = ":loud_sound:"

        await ctx.send(f"{volume_emote} Volume is set to {volume}%")

    # -------------------------------- ANCHOR LIST ------------------------------- #
    # Displays whole queue in an embed. Also leverages slash components to enable interaction. 
    # Skip pages / clear items / skip to particular tracks without using more commands. 

    @cog_ext.cog_slash(
        name="list",
        description="Displays an interactive list of songs in the queue",
        guild_ids=cfg['guild_ids'],
        options=[
            create_option(
                name="page",
                description="Create list on a specific page from 1 to <max pages> (check /list if you arent sure).",
                option_type=int,
                required=False
            )
        ]
    )
    async def list(self, ctx: SlashContext, page: int=1):
        player = await self.ensure_voice(ctx)
        if not player:
            return
        else:
            logging.info(f"[{ctx.author.name}" + (f"#{ctx.author.discriminator}" if ctx.author.discriminator else "#0000") + f"] Fetching queue list...")

        pages = player.fetch('pages')
        if page > pages:
            if pages > 0:
                await ctx.send(f"Page #{page} too high. Queue is only {pages} pages long.")
            else:
                await ctx.send("Queue is empty - no list to show.")
            return

        components = []

        list_buttons = [
            manage_components.create_button(
                style=discord_slash.ButtonStyle.primary,
                label="<",
                custom_id="list_page_prev"
            ),
            manage_components.create_button(
                style=discord_slash.ButtonStyle.primary,
                label=">",
                custom_id="list_page_next"
            )
        ]

        button_row = manage_components.create_actionrow(*list_buttons)
        components.append(button_row)

        embed = self.embed_list(player, page)
        message = await ctx.send(embed=embed, components=components)
        await message.edit(content=message.content)

    # -------------------------------- ANCHOR NOW -------------------------------- #
    # Displays details of the current song including playtime in a handy ascii layout
    
    @cog_ext.cog_slash(
        name="now",
        description="Display info on the current song",
        guild_ids=cfg['guild_ids']
    )
    async def now(self, ctx: SlashCommand):
        player = await self.ensure_voice(ctx)
        if not player:
            return
        else:
            logging.info(f"[{ctx.author.name}" + (f"#{ctx.author.discriminator}" if ctx.author.discriminator else "#0000") + f"] Fetching current song details...")

        embed = await self.embed_track(
            ctx, 
            player.current, 
            "Info requested", 
            len(player.queue), 
            footer=util.seek_bar(player) + " (paused)" if player.paused else ""
        )
        await ctx.send(embed=embed)

    # -------------------------------- ANCHOR SKIP ------------------------------- #
    # Skip current song or to a specific song in queue with the optional 'index' 
    # value.

    @cog_ext.cog_slash(
        name="skip",
        description="Skips current track.",
        guild_ids=cfg['guild_ids'],
        options=[
            manage_commands.create_option(
                name="index",
                description="Specify place in queue to skip to.",
                option_type=int,
                required=False
            )
        ]
    )
    async def skip_command(self, ctx: SlashCommand, index: int=None):
        player = await self.ensure_voice(ctx)
        if not player:
            return
        
        if index:
            await self.skip(ctx, player, index=index)

        else:
            await self.skip(ctx, player)

    # -------------------------------- ANCHOR JUMP ------------------------------- #
    # Jumps ahead to a specific index in the queue and when finished playing resumes
    # the normal queue

    @cog_ext.cog_slash(
        name="jump",
        description="Jumps to a specific song in the queue and resumes normal play afterward.",
        guild_ids=cfg['guild_ids'],
        options=[
            manage_commands.create_option(
                name="index",
                description="The specific song to jump to. Use /list to find this.",
                option_type=int,
                required=True
            )
        ]
    )
    async def jump(self, ctx: SlashCommand, index: int):
        player = await self.ensure_voice(ctx)
        if not player:
            return

        await self.skip(ctx, player, index, trim_queue=False)

    # ------------------------------- ANCHOR CLEAR ------------------------------- #
    # Clears the queue without making boomer leave the call. 

    @cog_ext.cog_slash(
        name="clear",
        description="Clears current queue.",
        guild_ids=cfg['guild_ids'],
        options=[
            manage_commands.create_option(
                name="index",
                description="Specify single song in queue to clear.",
                option_type=int,
                required=False
            )
        ]
    )
    async def clear_command(self, ctx: SlashContext, index: int=None):
        player = await self.ensure_voice(ctx)
        if not player:
            return
        else:
            logging.info(f"[{ctx.author.name}" + (f"#{ctx.author.discriminator}" if ctx.author.discriminator else "#0000") + f"] Clearing " + f"item with index {index}..." if index else "whole queue...")
        
        if not index:
            await self.clear(ctx)

        else:
            if index <= 0:
                await ctx.send(":warning: That index is too low! Queue starts at #1.", hidden=True)
                logging.warn(f"Index too low! Expected: >=1. Recieved: {index}")
                return

            elif index > len(player.queue):
                await ctx.send(f":warning: That index is too high! Queue only {len(player.queue)} items long.", hidden=True)
                logging.warn(f"Index too high! Expected: <= {len(player.queue)}. Recieved: {index}")
                return

            else:
                await self.clear(ctx, index - 1)


    # ------------------------------- ANCHOR REPEAT ------------------------------ #
    # Repeat either the current track or the entire playlist with a subcommand 'queue'

    # Single track
    @cog_ext.cog_subcommand(
        base="repeat",
        name="track",
        description="Repeats current song.",
        guild_ids=cfg['guild_ids']
    )
    async def loop(self, ctx: SlashCommand):
        player = await self.ensure_voice(ctx)
        if not player:
            return
        else:
            logging.info(f"[{ctx.author.name}" + (f"#{ctx.author.discriminator}" if ctx.author.discriminator else "#0000") + f"] Changing repeat state...")

        if player.fetch('repeat_one'):
            player.store('repeat_one', None)
            await ctx.send(":arrow_forward: Stopped repeating track.")
            logging.info(f"Repeat once disabled.")
        else:
            track = self.get_playing(player)
            player.store('repeat_one', track)
            await ctx.send(":repeat_one: Current track now repeating.")
            logging.info(f"Repeat once enabled")

    # Whole queue
    @cog_ext.cog_subcommand(
        base="repeat",
        name="queue",
        description="Repeats entire queue.",
        guild_ids=cfg['guild_ids']
    )
    async def loop_queue(self, ctx: SlashCommand):
        player = await self.ensure_voice(ctx)
        if not player:
            return
        else:
            logging.info(f"[{ctx.author.name}" + (f"#{ctx.author.discriminator}" if ctx.author.discriminator else "#0000") + f"] Changing repeat state...")

        player.set_repeat(not player.repeat)
        if player.repeat:
            await ctx.send(":repeat: Current queue now repeating.")
            logging.info(f"Repeat queue enabled")
        else:
            await ctx.send(":arrow_forward: Stopped repeating queue.")
            logging.info(f"Repeat queue disabled")

    # ------------------------------ ANCHOR SHUFFLE ------------------------------ #
    # Shuffles current queue on and off

    @cog_ext.cog_slash(
        name="shuffle",
        description="Shuffles the current queue. Works well with /repeat queue.",
        guild_ids=cfg['guild_ids']
    )
    async def shuffle(self, ctx: SlashCommand):
        player = await self.ensure_voice(ctx)
        if not player:
            return
        else:
            logging.info(f"[{ctx.author.name}" + (f"#{ctx.author.discriminator}" if ctx.author.discriminator else "#0000") + f"] Changing shuffle state...")

        if player.shuffle:
            player.set_shuffle(False)
            await ctx.send(":arrow_forward: Stopped shuffling.")
            logging.info(f"Shuffle state disabled")
        else:
            player.set_shuffle(True)
            await ctx.send(":twisted_rightwards_arrows: Current queue now shuffling.")
            logging.info(f"Shuffle state enabled")

    # --------------------------------- !SECTION --------------------------------- #
        
    # ---------------------------------------------------------------------------- #
    #                           SECTION[id=admin] -ADMIN                           #
    # ---------------------------------------------------------------------------- #

    # -------------------------------- ANCHOR DIE -------------------------------- #
    # Also disconnects him and clears queue.

    @cog_ext.cog_slash(
        name="die",
        description="Disconnects and shuts down Boomer safely",
        guild_ids=cfg['guild_ids'],
        default_permission=False,
        permissions={
            cfg['guild_ids'][0]: [
                create_permission(cfg['owner_id'], SlashCommandPermissionType.USER, True)
            ]
        }
    )
    async def _die(self, ctx: SlashContext):
        player = self.fetch_player(ctx)

        if player:
            player.queue.clear()
            await player.stop()
            await ctx.guild.change_voice_state(channel=None)

        await self.update_status(player)
        await ctx.send(f"My battery is low and it's getting dark :(")
        logging.info(f"[{ctx.author.name}" + (f"#{ctx.author.discriminator}" if ctx.author.discriminator else "#0000") + f"] Killed boomer.")
        await ctx.bot.close()
        return

    # ---------------------------- TODO REPORT COMMAND --------------------------- #

    # --------------------------------- !SECTION --------------------------------- #

def setup(bot):
    bot.add_cog(Music(bot))
