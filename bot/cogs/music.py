import asyncio
import re
import __main__
import time
import math
from discord import emoji, permissions, player
import discord_slash
from discord_slash.client import SlashCommand
from discord_slash.context import ComponentContext
from discord_slash.model import SlashCommandPermissionType
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

url_rx = re.compile(r'https?://(?:www\.)?.+')
cfg = config.load_config()

# ------------------------------- ANCHOR CLASS ------------------------------- #

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.emojis = {}
        for emoji in cfg['emojis']:
            self.emojis[emoji] = cfg['emojis'][emoji]
            
        bot.lavalink = lavalink.Client(cfg['bot_id'])
        # Host, Port, Password, Region, Name
        cfg_lava = cfg['lavalink']
        bot.lavalink.add_node(cfg_lava['ip'], cfg_lava['port'], cfg_lava['pwd'], cfg_lava['region'], cfg_lava['name'])
        bot.add_listener(bot.lavalink.voice_update_handler,'on_socket_response')

        self.looping = False

        lavalink.add_event_hook(self._hooks)

    # ---------------------------------------------------------------------------- #
    #                         SECTION[id=callbacks] -EVENTS                        #
    # ---------------------------------------------------------------------------- #

    # ---------------------------- ANCHOR PLAYER HOOKS --------------------------- #
    # Runs whenever an event is raised by the player. Run things like EndQueue and 
    # EndTrack etc. 

    async def _hooks(self, event):

        if isinstance(event, lavalink.events.TrackEndEvent):

            player = event.player
            track = player.fetch('repeat_one')
            if track:
                player.add(requester=cfg['bot_id'], track=track, index=0)

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
                await player.queue.clear()
                await player.stop()
                await guild.change_voice_state(channel=None)
                return print('Nothing found for idle music! look for a new video.')

            player.store('idle', True)
            track = results['tracks'][0]
            player.add(requester=cfg['bot_id'], track=track)
            if not player.is_playing:
                await player.play()

    # ---------------------------- ANCHOR LIST BUTTONS --------------------------- #
    # Callbacks for list button slash commands

    # Go back a page
    @cog_ext.cog_component()
    async def list_page_prev(self, btx: ComponentContext):
        page_string = btx.origin_message.embeds[0].description
        page = [int(s) for s in page_string.split() if s.isdigit()][0]

        await btx.send(f"{page}")

    # Go forward a page
    @cog_ext.cog_component()
    async def list_page_next(self, btx: ComponentContext):
        await btx.send("You pressed the next button!")

    # Clear selected track
    @cog_ext.cog_component()
    async def list_track_clear(self, btx: ComponentContext):
        await btx.send("You pressed the clear button!")

    # Jump to selected track
    @cog_ext.cog_component()
    async def list_track_jump(self, btx: ComponentContext):
        await btx.send("You pressed the jump button!")

    # Select track multichoice
    @cog_ext.cog_component()
    async def list_track_select(self, btx: ComponentContext):
        player = self._fetch_player(btx)
        player.store('list_track_selected', player.queue[int(btx.values[0])])

    # --------------------------------- !SECTION --------------------------------- #

    # ---------------------------------------------------------------------------- #
    #                       SECTION[id=helpers] -HELPERS                           #
    # ---------------------------------------------------------------------------- #

    # ---------------------------- ANCHOR FETCHPLAYER ---------------------------- #
    # Returns the bots player if one exists otherwise sets up the default one and
    # returns that

    def _fetch_player(self, ctx: SlashContext) -> lavalink.DefaultPlayer:
        # Create returns a player if one exists, otherwise creates.
        return self.bot.lavalink.player_manager.create(
            ctx.guild.id, endpoint=str(ctx.guild.region)
        )

    # ---------------------------- ANCHOR ENSUREVOICE ---------------------------- #
    # Makes sure boomer joins a voice channel if commands that need it are queued (
    # i.e. anything that plays or queues a song). Otherwise makes sure you're in the 
    # the same voice channel as the bot to run things.

    async def _ensure_voice(self, ctx: SlashContext) -> lavalink.DefaultPlayer or None:
        # This check ensures that the bot and command author are in the same voicechannel.

        player = self._fetch_player(ctx)

        # These are commands that require the bot to join a voicechannel.
        should_connect = ctx.command in ('play','ok','lofi')

        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send('Join a voicechannel first.')
            return

        if not player.is_connected:
            if not should_connect:
                await ctx.send('Not connected.')
                return

            player.store('channel', ctx.channel.id)
            player.store('voice', ctx.author.voice.channel)
            await ctx.guild.change_voice_state(channel=ctx.author.voice.channel)

            return player
        else:
            if int(player.channel_id) != ctx.author.voice.channel.id:
                await ctx.send(f"You need to be in <#{player.channel_id}> to do that.")

            return player

    def _get_playing(self, player: lavalink.DefaultPlayer) -> lavalink.AudioTrack:
        if player.current:
            track = player.current
        elif self.looping:
            track = player.fetch('repeat_one')
        else:
            track = player.queue[0]
        return track

    # -------------------------------- ANCHOR PLAY ------------------------------- #
    # Core method for this class. Takes query and uses lavalink to grab / enqueue results.
    # Plays frist result directly if nothign else in in the queue and kills idle state / resets
    # volume if needed.

    async def _play(self, ctx: SlashContext, query: str):
        # Adds a song to the queue, plays the queue if it hasn't been started, or adds to the queue if a song is already playing.
        player = await self._ensure_voice(ctx)
        if not url_rx.match(query):
            query = f"ytsearch:{query}"

        results = await player.node.get_tracks(query)

        if not results or not results['tracks']:
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
                    text=f"Songs are #{len(player.queue) + 1} to #{len(player.queue) + len(tracks)} in queue."
                )

            # Add all tracks to the queue
            for track in tracks:
                player.add(requester=ctx.author.id, track=track)

        else:
            # Grab track info
            track = results['tracks'][0]
            info = track["info"]

            # Populate embed
            embed.set_author(
                name=f"Song queued by {ctx.author.display_name}: ",
                url=info['uri'],
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

        await ctx.send(embed=embed)

        # Start playing if no song is in queue
        if player.fetch('idle'):
            player.store('idle', False)
            await player.play()
            await player.set_volume(player.fetch('volume_guild'))
        elif not player.is_playing:
            await player.set_volume(cfg['music']['volume_default'])
            await player.play()

        player.store(
            'pages',
            math.ceil(len(player.queue) / cfg['music']['queue_page_len'])
        )

    # ----------------------------- ANCHOR MAKE LIST ----------------------------- #
    # Used by the list command to put a queue summary together

    def _make_list(self, player: lavalink.DefaultPlayer, page: int) -> discord.Embed:
        queue_start = (page - 1) * cfg['music']['queue_page_len']
        queue_end = queue_start + ( cfg['music']['queue_page_len'] - 1) if page < player.fetch('pages') else len(player.queue) - queue_start - 1
        if queue_end == 0:
            queue_end += 1

        track = self._get_playing(player)

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
            try:
                track: lavalink.AudioTrack = player.queue[i]
                play_time = lavalink.format_time(track.duration)

                # Strip hour from a video if its less than an hour long
                if play_time.startswith("00:"):
                    play_time = play_time.replace("00:", "")

                embed.add_field(
                    name=f"{i + 1}. *{track.title}*",
                    value=f"Play time: {play_time}"
                )
            except IndexError:
                print("Index Out Of Range: _make_list")
                print(
                    f"Queue len: {len(player.queue)} | Page: {page} | Queue_start: {queue_start} | Queue_end: {queue_end}| Index: {i}")

        embed.set_footer(
            text=f"<> for page +/-, dropdown to select track, ❌/⏭️ to clear/skip to track."
        )

        return embed

    # ----------------------------- ANCHOR MAKE EMBED ---------------------------- #
    # Constructs and returns an embed for a single track. Action gets prepended to author title

    async def _make_embed(self, ctx: SlashContext, track: lavalink.AudioTrack, action: str , queue_len: int) -> discord.Embed:
        # Construct feedback embed
        embed = discord.Embed(
            color=discord.Color.blurple(),
            title=track.title,
            description=f"Song by: {track.author}",
        )
        embed.set_author(
            name=f"{action} by {ctx.author.display_name}. Now playing: ",
            url=track.uri,
            icon_url=ctx.author.avatar_url
        )
        embed.set_thumbnail(
            url=f"https://i.ytimg.com/vi/{track.identifier}/mqdefault.jpg"
        )
        embed.set_footer(
            text=f"Songs remaining in queue: {queue_len}"
        )

        return embed

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
        guild_ids=[cfg['guild_id']]
    )
    async def _okboomer(self, ctx: SlashContext):
        player = await self._ensure_voice(ctx)
        
        if player.is_playing:
            await ctx.send(f"I'm already in <#{player.fetch('voice').id}> zoomer.")
        else:
            await ctx.send(f"Joined <#{player.fetch('voice').id}>")
            await player.set_volume(10)
            await self._hooks(lavalink.QueueEndEvent(player))

    # ----------------------------- ANCHOR LOFI RADIO ---------------------------- #
    # Simple shortcut for lofi beats because lavalink doesnt like searching for livestreams for some reason

    @cog_ext.cog_subcommand(
        base="lofi",
        name="radio",
        description="Plays the Lofi Hip Hop radio livestream.",
        guild_ids=[cfg['guild_id']]
    )
    async def _lofi_radio(self, ctx: SlashContext):
        query = "https://www.youtube.com/watch?v=5qap5aO4i9A"
        await self._play(ctx, query)

    # --------------------------------- !SECTION --------------------------------- #

    # ---------------------------------------------------------------------------- #
    #                        SECTION[id=commands] -COMMANDS                        #
    # ---------------------------------------------------------------------------- #

    # -------------------------------- ANCHOR PLAY ------------------------------- #
    # Calls self._play and passes along song request / message context

    @cog_ext.cog_slash(
        name="play",
        description="Plays a song from given query / url.",
        options=[
            create_option(
                name="song",
                description="Searches for a song on YouTube. Plays URL directly if given",
                option_type=str,
                required=True
            )
        ]
    )
    async def _play_command(self, ctx: SlashContext, song: str):
        await self._play(ctx, song)

    # ------------------------------- ANCHOR LEAVE ------------------------------- #
    # Leave voice chat if in one. Also resets the queue

    @cog_ext.cog_slash(
        name="leave",
        description="Disconnects Boomer from voice and clears the queue",
        guild_ids=[cfg['guild_id']]
    )
    async def _leave(self, ctx: SlashContext):
        player = await self._ensure_voice(ctx)
        if not player:
            return

        if player:
            player.queue.clear()
            await player.stop()
            await ctx.guild.change_voice_state(channel=None)
            await ctx.send(f":wave: Leaving <#{player.fetch('voice').id}> and clearing queue.")

    # ------------------------------- ANCHOR VOLUME ------------------------------ #
    # Print volume, or ncrease / decrease volume. Capped at 0-50 (displayed as 0-100)
    # for normal users and 0-1000 for the server owner.

    @cog_ext.cog_slash(
        name="volume",
        description="See Boomer's volume level. Add level to change it.",
        guild_ids=[cfg['guild_id']],
        options=[
            create_option(
                name="level",
                description="Volume level from 0% to 100%",
                option_type=int,
                required=False
            )
        ]
    )
    async def _volume(self, ctx: SlashContext, level: int = None):
        player = await self._ensure_voice(ctx)
        volume = level # Make dealing with volume more sensible
        if not player:
            return

        if volume:
            if ctx.author.id != cfg['owner_id']:
                volume = util.clamp(volume, 0, 100)

            await player.set_volume(math.ceil(volume / 2))
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
        guild_ids=[cfg['guild_id']],
        options=[
            create_option(
                name="page",
                description="Create list on a specific page from 1 to <max pages> (check /list if you arent sure).",
                option_type=int,
                required=False
            )
        ]
    )
    async def _list(self, ctx: SlashContext, page: int=1):
        player = await self._ensure_voice(ctx)
        if not player:
            return

        pages = player.fetch('pages')
        if page > pages:
            if pages > 0:
                await ctx.send(f"Page #{page} too high. Queue is only {pages} pages long.")
            else:
                await ctx.send("Queue is empty - no list to show.")
            return

        queue_start = (page - 1) * cfg['music']['queue_page_len']
        queue_end = queue_start + ( cfg['music']['queue_page_len'] - 1) if page < player.fetch('pages') else len(player.queue) - queue_start - 1

        options = components = []
        for i in range(queue_start, queue_end + 1):
            options.append(manage_components.create_select_option(
                label=f"{i + 1}. {player.queue[i].title}",
                value=f"{i}"
            ))

        if len(options) > 0:
            list_select = [
                manage_components.create_select(
                    options=options,
                    custom_id="list_track_select",
                    placeholder="Select one of the tracks on the current page",
                )
            ]

            select_row = manage_components.create_actionrow(list_select)
            components.append(select_row)

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
            ),
            manage_components.create_button(
                style=discord_slash.ButtonStyle.danger,
                label="x",
                custom_id="list_track_clear"
            ),
            manage_components.create_button(
                style=discord_slash.ButtonStyle.success,
                label=">>",
                custom_id="list_track_jump",
            )
        ]

        button_row = manage_components.create_actionrow(*list_buttons)
        components.append(button_row)

        print(components)

        embed = self._make_list(player, page)
        await ctx.send(embed=embed, components=components)

    # -------------------------------- ANCHOR SKIP ------------------------------- #
    # Skip current song or to a specific song in queue with the optional 'index' 
    # value.

    @cog_ext.cog_slash(
        name="skip",
        description="Skips current track.",
        guild_ids=[cfg['guild_id']]
    )
    async def _skip(self, ctx: SlashCommand):
        player = await self._ensure_voice(ctx)
        if not player:
            return

        embed_action = "Track skipped"

        if len(player.queue) > 0 or player.fetch('repeat_one'):
            # Get next track in playlist info

            if player.fetch('repeat_one'):
                next_track = player.fetch('repeat_one')
                queue_len = len(player.queue)
                embed = await self._make_embed(
                    ctx,
                    track=next_track,
                    action=embed_action,
                    queue_len=queue_len
                )
                await ctx.send(":repeat_one: Looping enabled - repeating song.", embed=embed)
                await player.seek(0)

            elif player.shuffle:
                await player.skip()
                next_track = player.current
                embed = await self._make_embed(
                    ctx,
                    track=next_track,
                    action=embed_action,
                    queue_len=len(player.queue)
                )
                await ctx.send(embed=embed)

            else:
                next_track = player.queue[0]
                embed = await self._make_embed(
                    ctx,
                    track=next_track,
                    action=embed_action,
                    queue_len=len(player.queue)
                )
                await ctx.send(embed=embed)
        else:
            await ctx.send(message=":notepad_spiral: End of queue - time for your daily dose of idle tunes.")


    # -------------------------------- ANCHOR LOOP ------------------------------- #
    # Loop either the current track or the entire playlist with a subcommand 'queue'

    # Single track
    @cog_ext.cog_subcommand(
        base="loop",
        name="track",
        description="Repeats current song.",
        guild_ids=[cfg['guild_id']]
    )
    async def _loop(self, ctx: SlashCommand):
        player = await self._ensure_voice(ctx)
        if not player:
            return

        if player.fetch('repeat_one'):
            player.store('repeat_one', None)
            await ctx.send(":arrow_forward: Stopped looping track.")
        else:
            track = self._get_playing(player)
            player.store('repeat_one', track)
            await ctx.send(":repeat_one: Current track now looping.")

    # Whole queue
    @cog_ext.cog_subcommand(
        base="loop",
        name="queue",
        description="Repeats entire queue.",
        guild_ids=[cfg['guild_id']]
    )
    async def _loop_queue(self, ctx: SlashCommand):
        player = await self._ensure_voice(ctx)
        if not player:
            return

        player.set_repeat(not player.repeat)
        if player.repeat:
            await ctx.send(":repeat: Current queue now looping.")
        else:
            await ctx.send(":arrow_forward: Stopped looping queue.")

    # ------------------------------ ANCHOR SHUFFLE ------------------------------ #
    # Shuffles current queue on and off

    @cog_ext.cog_slash(
        name="shuffle",
        description="Shuffles the current queue. Works well with /loop queue.",
        guild_ids=[cfg['guild_id']]
    )
    async def _shuffle(self, ctx: SlashCommand):
        player = await self._ensure_voice(ctx)
        if not player:
            return
        
        if player.shuffle:
            player.set_shuffle(False)
            await ctx.send(":arrow_forward: Stopped looping shuffling.")
        else:
            player.set_shuffle(True)
            await ctx.send(":twisted_rightwards_arrows: Current queue now shuffled.")

    # --------------------------------- !SECTION --------------------------------- #
        
    # ---------------------------------------------------------------------------- #
    #                           SECTION[id=admin] -ADMIN                           #
    # ---------------------------------------------------------------------------- #

    # -------------------------------- ANCHOR DIE -------------------------------- #
    # Also disconnects him and clears queue.

    @cog_ext.cog_slash(
        name="die",
        description="Disconnects and shuts down Boomer safely",
        guild_ids=[cfg['guild_id']],
        default_permission=False,
        permissions={
            cfg['guild_id']: [
                create_permission(cfg['owner_id'], SlashCommandPermissionType.USER, True)
            ]
        }
    )
    async def _die(self, ctx: SlashContext):
        player = self._fetch_player(ctx)

        if player:
            player.queue.clear()
            await player.stop()
            await ctx.guild.change_voice_state(channel=None)
        await ctx.send(f"My battery is low and it's getting dark {self.emojis['emotesad']}")
        await ctx.bot.logout()

    # --------------------------------- !SECTION --------------------------------- #

def setup(bot):
    bot.add_cog(Music(bot))
