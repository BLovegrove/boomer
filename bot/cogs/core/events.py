# ---------------------------------- Imports --------------------------------- #
import logging
from typing import List

import discord
from discord.ext import commands
from discord_slash.context import ComponentContext
from discord_slash import cog_ext
import lavalink

from ... import config
from .voice import VoiceStateManager as VSM

# ---------------------------------- Config ---------------------------------- #
cfg = config.load_config()

# --------------------------------- Cog class -------------------------------- #
class Events(commands.Cog):
    def __init__(self, bot):
        self.bot: discord.Client = bot
        self.VSM: VSM = bot.get_cog('VoiceStateManager')
        
        lavalink.add_event_hook(self.hooks)

    # ---------------------------------------------------------------------------- #
    #                              methods / Commands                              #
    # ---------------------------------------------------------------------------- #

    # -------------------------- ANCHOR CH LEFT/SWAPPED -------------------------- #
    # Fires every time a user leaves a channel and that channel matches the channel 
    # stored by the bot player + has no members left in it.
    # Also tracks channel changes to update player 'voice' attribute etc.

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):

        player: lavalink.DefaultPlayer = self.bot.lavalink.player_manager.create(
            member.guild.id, endpoint=str(member.guild.region)
        )

        if (player.fetch('voice')):
            if (before.channel):
                if (not after.channel or after.channel.id != player.fetch('voice').id):
                    if (before.channel.id == player.fetch('voice').id):
                        if (len(player.fetch('voice').voice_states.keys()) == 1):
                            await self.VSM.disconnect(player, member.guild)
                            logging.info(f"[Boomer#7010] No more members left in channel! Cleaning up and leaving call.")
                else:
                    player.store('voice', member.voice.channel)

    # ---------------------------- ANCHOR PLAYER HOOKS --------------------------- #
    # Runs whenever an event is raised by the player. Run things like EndQueue and 
    # EndTrack etc. 

    async def hooks(self, event):

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
                await self.VSM.update_status(player)

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


def setup(bot):
    bot.add_cog(Events(bot))
