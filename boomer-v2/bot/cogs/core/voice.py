# ---------------------------------- Imports --------------------------------- #
import re

import discord
from discord.ext import commands
from discord_slash import SlashContext
import lavalink
from lavalink import DefaultPlayer

from ... import config

# ---------------------------------- Config ---------------------------------- #
cfg = config.load_config()
standard_rx = re.compile(r'https?://(?:www\.)?.+')

# --------------------------------- Cog class -------------------------------- #
class VoiceStateManager(commands.Cog):
    def __init__(self, bot):
        self.bot: discord.Client = bot

    # ---------------------------------------------------------------------------- #
    #                              Methods / Commands                              #
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

    async def ensure_voice(self, ctx: SlashContext) -> lavalink.DefaultPlayer:
        # This check ensures that the bot and command author are in the same voicechannel.

        player = self.fetch_player(ctx)

        # These are commands that require the bot to join a voicechannel.
        should_connect = ctx.command in ('play','ok','lofi','test','best','load','die')

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
        
    # ----------------------------- ANCHOR DISCONNECT ---------------------------- #
    # Safely disconnects the bot from it's voice channel and clears up / resets any 
    # relevent settings.

    async def disconnect(self, player: lavalink.DefaultPlayer, guild: discord.Guild):

        player.queue.clear()
        await player.stop()
        await guild.change_voice_state(channel=None)
        player.store('repeat_one', None)
        player.set_repeat(False)
        player.set_shuffle(False)
        await player.set_volume(cfg['music']['volume_default'])
        await self.update_status(player)
    
VSM = VoiceStateManager

def setup(bot):
    bot.add_cog(VoiceStateManager(bot))