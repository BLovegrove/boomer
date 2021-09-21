from typing import Mapping, Optional
from discord import embeds
from discord.ext import commands
import discord
from discord_slash import cog_ext, SlashContext
import asyncio
from discord_slash.model import OptionData
from discord_slash.utils.manage_commands import create_option
import youtube_dl
import logging
import toml
from urllib import request
from ..video import Video

FFMPEG_BEFORE_OPTS = '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
config = toml.load("./config.toml")
GUILD = config["lamz"]

async def audio_playing(ctx):
    # Checks that audio is currently playing before continuing.
    client = ctx.guild.voice_client
    if client and client.channel and client.source:
        return True
    else:
        await ctx.send("Not currently playing any audio.")


async def in_voice_channel(ctx):
    # Checks that the command sender is in the same voice channel as the bot.
    voice = ctx.author.voice
    bot_voice = ctx.guild.voice_client
    if voice and bot_voice and voice.channel and bot_voice.channel and voice.channel == bot_voice.channel:
        return True
    else:
        await ctx.send("You need to be in the channel to do that.")

# Bot commands to help play music.
class Music(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.config = config[__name__.split(".")[-1]] # retrieve module name, find config entry
        self.states = {}
        self.looping = False

    def get_state(self, guild):
        # Gets the state for `guild`, creating it if it does not exist.
        if guild.id in self.states:
            return self.states[guild.id]
        else:
            self.states[guild.id] = GuildState()
            return self.states[guild.id]

    @cog_ext.cog_slash(
        name="leave",
        description="Disconnect from the currently active voice channel, if there is one.",
        guild_ids=[GUILD]
    )
    async def _leave(self, ctx: SlashContext):
        if ctx.channel.permissions_for(ctx.author).administrator or discord.utils.get(ctx.guild.roles, id=636752904652587019) in ctx.author.roles:
            client = ctx.guild.voice_client
            state = self.get_state(ctx.guild)
            if client and client.channel:
                await ctx.send(":wave: Leaving voice and clearing queue.")
                await client.disconnect()
                state.playlist = []
                state.now_playing = None
                self.looping = False
            else:
                await ctx.send("Not in a voice channel.")
        else:
            await ctx.send("You don't have permission to disconnect the bot.")

    @cog_ext.cog_slash(
        name="volume",
        description="Change bot playback volume (0-100).",
        guild_ids=[GUILD]
    )
    async def _volume(self, ctx: SlashContext, volume: int):
        if await audio_playing(ctx) and await in_voice_channel(ctx):
            state = self.get_state(ctx.guild)

            # make sure volume is nonnegative
            if volume < 0:
                volume = 0

            max_vol = 100
            if max_vol > -1:  # check if max volume is set
                # clamp volume to [0, max_vol]
                if volume > max_vol:
                    volume = max_vol

            client = ctx.guild.voice_client

            state.volume = float(volume) / 100.0
            client.source.volume = state.volume  # update the AudioSource's volume to match
            await ctx.send(f":loud_sound: Volume changed to {volume}%")

    @cog_ext.cog_slash(
        name="skip",
        description="Skips current song.",
        guild_ids=[GUILD]
    )
    async def skip(self, ctx: SlashContext):
        if await audio_playing(ctx) and await in_voice_channel(ctx):
            state = self.get_state(ctx.guild)
            client = ctx.guild.voice_client
            if ctx.channel.permissions_for(ctx.author).administrator or discord.utils.get(ctx.guild.roles, id=636752904652587019) in ctx.author.roles:
                if not self.looping:
                    await ctx.send(":next_track: Skipping track.")
                else:
                    await ctx.send(":repeat_one: Looping track again.")
                client.stop()
            else:
                await ctx.send("You don't have permission to skip.")

    def _play_song(self, client, state, song, loading_message=None, author=None):
        state.now_playing = song
        channel = self.bot.get_channel(state.output_channel)
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(song.stream_url, before_options=FFMPEG_BEFORE_OPTS), volume=state.volume)

        def after_playing(err):
            if not self.looping:
                if len(state.playlist) > 0:
                    next_song = state.playlist.pop(0)
                    self._play_song(client, state, next_song)
                else:
                    asyncio.run_coroutine_threadsafe(client.disconnect(), self.bot.loop)
            else:
                self._play_song(client, state, state.now_playing)

        client.play(source, after=after_playing)
        if loading_message != None and author != None:
            asyncio.run_coroutine_threadsafe(
                loading_message.edit(content=":arrow_forward: Song found. Now playing:", embeds=[state.now_playing.get_embed(author)]),
                self.bot.loop
            )

    @cog_ext.cog_slash(
        name="list",
        description="Lists current play queue",
        guild_ids=[GUILD]
    )
    async def _list(self, ctx: SlashContext,):
        if not await audio_playing(ctx):
            await ctx.send("No queue to display.")
        else:
            state = self.get_state(ctx.guild)
            await ctx.send(self._queue_text(state.playlist, ctx))

    def _queue_text(self, queue, ctx):
        # Returns a block of text describing a given song queue.
        if len(queue) >= 0:
            message = [f"{len(queue)} songs in queue:"]
            state = self.get_state(ctx.guild)
            message += [f"  0. **{state.now_playing.title}** :loud_sound:"]
            message += [
                f"  {index+1}. **{song.title}**"
                for (index, song) in enumerate(queue)
            ]  # add individual songs
            return "\n".join(message)
        else:
            return "The play queue is empty."

    @cog_ext.cog_slash(
        name="clear",
        description="Clears the current queue without leaving channel.",
        options=[
            create_option(
                option_type=4,
                name="index",
                description="Clear specific song from the queue",
                required=False
            )
        ],
        guild_ids=[GUILD],
    )
    async def _clear(self, ctx: SlashContext, index:int=None):
        if await audio_playing(ctx):
            if ctx.channel.permissions_for(ctx.author).administrator or discord.utils.get(ctx.guild.roles, id=636752904652587019) in ctx.author.roles:
                state = self.get_state(ctx.guild)
                if index == None:
                    state.playlist = []
                    await ctx.send(":x: Queue cleared.")
                else:
                    index -= 1
                    if index < len(state.playlist) and index >= 0:
                        message = await ctx.send(f":x: Queue item {index + 1} cleared.\n:musical_note: {state.playlist[index].title}")
                        state.playlist.pop(index)
                        await message.edit(
                            content=message.content + f"\n\n{self._queue_text(state.playlist, ctx)}"
                        )
                    else:
                        await ctx.send(":warning: Index out of bounds. Might want to double check /list.")
            else:
                await ctx.send("You don't have permission to clear queue.")

    @cog_ext.cog_slash(
        name="play",
        description="Plays song from given search term or URL.",
        guild_ids=[GUILD]
    )
    async def _play(self, ctx: SlashContext, song):

        client = ctx.guild.voice_client
        state = self.get_state(ctx.guild) # get the guild's state
        state.output_channel = ctx.channel_id

        if ctx.channel.permissions_for(ctx.author).administrator or discord.utils.get(ctx.guild.roles, id=636752904652587019) in ctx.author.roles:
            if client and client.channel:
                loading_message = await ctx.send("Grabbing song <a:loading:889376383338422274>")
                try:
                    video = Video(song)
                    state.playlist.append(video)
                except youtube_dl.DownloadError as e:
                    logging.warn(f"Error downloading video: {e}")
                    await ctx.send("There was an error downloading your video.")
                    return
                await loading_message.edit(content=":notepad_spiral: Soung found. Adding to queue:", embeds=[state.playlist[-1].get_embed(ctx.author)])
            else:
                if ctx.author.voice is not None and ctx.author.voice.channel is not None:
                    loading_message = await ctx.send("Grabbing song <a:loading:889376383338422274>")
                    channel = ctx.author.voice.channel
                    try:
                        video = Video(song)
                        client = await channel.connect()
                        self._play_song(client, state, video, loading_message, ctx.author)
                    except youtube_dl.DownloadError as e:
                        await ctx.send("There was an error downloading your video.")
                        return
                else:
                    await ctx.send("You need to be in a voice channel to do that.")
        else:
            await ctx.send("You don't have permission to play songs.")

    @cog_ext.cog_slash(
        name="loop",
        description="Loops the current track.",
        guild_ids=[GUILD]
    )
    async def _loop(self, ctx: SlashContext):
        if ctx.channel.permissions_for(ctx.author).administrator or discord.utils.get(ctx.guild.roles, id=636752904652587019) in ctx.author.roles:
            if self.looping:
                self.looping = False
                await ctx.send(":arrow_forward: Looping disabled. Continuing with queue.")
            else:
                self.looping = True
                await ctx.send(":repeat_one: Looping enabled. Repeating current track.")
        else:
            await ctx.send("You don't have permission to change loop status.")

def setup(bot):
    bot.add_cog(Music(bot))

class GuildState:
    # Helper class managing per-guild state.

    def __init__(self):
        self.volume = 0.2
        self.playlist = []
        self.now_playing = None
        self.output_channel = ""

