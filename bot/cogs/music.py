import asyncio
import re
import __main__
import time
import math
from discord import emoji, permissions, player
from discord_slash.client import SlashCommand
from discord_slash.model import SlashCommandPermissionType
from discord_slash.utils.manage_commands import create_option, create_permission
from lavalink.models import DefaultPlayer
from lavalink.utils import decode_track
from .. import config
from .. import util
import discord
import lavalink
from discord.ext import commands
from discord_slash import SlashContext, cog_ext

url_rx = re.compile(r'https?://(?:www\.)?.+')
cfg = config.load_config()

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

        lavalink.add_event_hook(self.track_hook)

    # Abuse prevention. Users not in voice channels, or not in the same voice channel as the bot cant touch it
    async def _in_same_channel(self, ctx: SlashContext):
        player = await self._ensure_voice(ctx)
        if ctx.author.voice and player.is_connected and ctx.author.voice.channel.id == int(player.channel_id):
            return True
        else:
            await ctx.send(f"Join <#{player.fetch('voice').id}> to do that.")
            return False

    # Create / get existing default player using context
    def _fetch_player(self, ctx: SlashContext) -> lavalink.DefaultPlayer:
        return self.bot.lavalink.player_manager.create(
            ctx.guild.id, endpoint=str(ctx.guild.region)
        )

    async def _ensure_voice(self, ctx: SlashContext) -> lavalink.DefaultPlayer or None:
        # This check ensures that the bot and command author are in the same voicechannel.

        player = self._fetch_player(ctx)
        # Create returns a player if one exists, otherwise creates.
        # This line is important because it ensures that a player always exists for a guild.

        # These are commands that require the bot to join a voicechannel.
        should_connect = ctx.command in ('play','ok','lofi','volume','skip','clear','list')

        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send('Join a voicechannel first.')
            return None

        if not player.is_connected:
            if not should_connect:
                await ctx.send('Not connected.')
                return None

            player.store('channel', ctx.channel.id)
            player.store('voice', ctx.author.voice.channel)
            await ctx.guild.change_voice_state(channel=ctx.author.voice.channel)

            return player
        else:
            if int(player.channel_id) != ctx.author.voice.channel.id:
                await ctx.send(f"You need to be in <#{ctx.author.voice.channel}>.")

            return player

    async def track_hook(self, event):
        # Play soft elevator music when no music is in queue
        if isinstance(event, lavalink.events.QueueEndEvent):

            guild_id = int(event.player.guild_id)
            guild = self.bot.get_guild(guild_id)

            player = event.player
            player.store('guild_volume', player.volume)
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
            await self.track_hook(lavalink.QueueEndEvent(player))

    @cog_ext.cog_slash(
        name="leave",
        description="Disconnects Boomer from voice and clears the queue",
        guild_ids=[cfg['guild_id']]
    )
    async def _leave(self, ctx: SlashContext):
        # Leave voice chat if in one. Also resets the queue
        player = await self._ensure_voice(ctx)

        if not self._in_same_channel(ctx):
            return

        if player:
            player.queue.clear()
            await player.stop()
            await ctx.guild.change_voice_state(channel=None)
            await ctx.send(f":wave: Leaving <#{player.fetch('voice').id}> and clearing queue.")

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
        volume = level

        if not self._in_same_channel(ctx):
            return

        if volume:
            if ctx.author.id != cfg['owner_id']:
                volume = util.clamp(volume, 0, 100)
                volume = math.ceil(volume / 2)

            await player.set_volume(volume)
        else:
            volume = player.volume

        if volume <= 33:
            volume_emote = ":speaker:"
        elif volume > 33 and volume <= 66:
            volume_emote = ":sound:"
        else:
            volume_emote = ":loud_sound:"
        await ctx.send(f"{volume_emote} Volume is set to {volume}%")

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
                url="https://tinyurl.com/boomermusic",
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
                    text=f"Song is #{len(player.queue) + 1} in queue.")

            # Add song to playlist
            player.add(requester=ctx.author.id, track=track)

        await ctx.send(embed=embed)

        # Start playing if no song is in queue
        if player.fetch('idle'):
            player.store('idle', False)
            await player.play()
            await player.set_volume(player.fetch('guild_volume'))
            player.delete('guild_volume')
        elif not player.is_playing:
            await player.set_volume(cfg['music']['volume_default'])
            await player.play()

    @cog_ext.cog_slash(
        name="skip",
        description="Skips current track.",
        guild_ids=[cfg['guild_id']]
    )
    async def _skip(self, ctx: SlashCommand):
        player = await self._ensure_voice(ctx)

        if not self._in_same_channel(ctx):
            return

        if len(player.queue) >= 1:
            # Get next track in playlist info
            next_track:lavalink.AudioTrack = player.queue[0]

            # Construct feedback embed
            embed = discord.Embed(
                color=discord.Color.blurple(), 
                title=next_track.title,
                description=f"Song by: {next_track.author}",
            )
            embed.set_author(
                name=f"Track skipped by {ctx.author.display_name}. Now playing: ",
                url=next_track.uri,
                icon_url=ctx.author.avatar_url
            )
            embed.set_thumbnail(
                url=f"https://i.ytimg.com/vi/{next_track.identifier}/mqdefault.jpg"
            )
            # TODO: Add footer describing remaining queue
            await ctx.send(embed=embed)
        else:
            await ctx.send(":notepad_spiral: End of queue - time for your daily dose of idle tunes.")
        await player.skip()

    @cog_ext.cog_subcommand(
        base="lofi",
        name="radio",
        description="Plays the Lofi Hip Hop radio livestream.",
        guild_ids=[cfg['guild_id']]
    )
    async def _lofi_radio(self, ctx: SlashContext):
        query = "https://www.youtube.com/watch?v=5qap5aO4i9A"
        await self._play(ctx, query)
        
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

def setup(bot):
    bot.add_cog(Music(bot))
