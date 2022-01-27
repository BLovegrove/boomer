# ---------------------------------- Imports --------------------------------- #
import logging
import re

import discord
from discord.ext import commands
from discord_slash import SlashContext
from lavalink import DefaultPlayer

from ... import config
from ... import spotify
from .voice import VoiceStateManager as VSM
from .queue import QueueManager as QM

# ---------------------------------- Config ---------------------------------- #
cfg = config.load_config()
standard_rx = re.compile(r'https?://(?:www\.)?.+')

# --------------------------------- Cog class -------------------------------- #    
class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.VSM: VSM = bot.get_cog('VoiceStateManager')
        self.QM: QM = bot.get_cog('QueueManager')
    
    # -------------------------------- ANCHOR PLAY ------------------------------- #
    # Core method for this class. Takes query and uses lavalink to grab / enqueue results.
    # Plays frist result directly if nothign else in in the queue and kills idle state / resets
    # volume if needed.

    async def play(self, ctx: SlashContext, query: str):
        player = await self.VSM.ensure_voice(ctx)
        if not player:
            return
        else:
            logging.info(f"[{ctx.author.name}" + (f"#{ctx.author.discriminator}" if ctx.author.discriminator else "#0000") + f"] Attempting to play song... Query: {query}")

        try:
            await ctx.defer()
        except:
            pass

        results = None

        if not standard_rx.match(query):
            query = f"ytsearch:{query}"
            results = await player.node.get_tracks(query)

        else:
            # Custom Spotify link handler
            if "open.spotify.com" in query:
                results = await spotify.spotify_query_handler(ctx, player, query)
            else:
                # Normal link handler (YouTube, Soundcloud, etc.)
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

        self.QM.update_pages(player)
        
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
                embed = await self.QM.embed_track(
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
                embed = await self.QM.embed_track(
                    ctx,
                    track=next_track,
                    action=embed_action,
                    queue_len=len(player.queue)
                )
                await ctx.send(embed=embed)

            else:
                if index:
                    index = index - 1 # Revert to index+1 for user readability
                    if index <= 0:
                        await ctx.send(":warning: That index is too low! Queue starts at #1.", hidden=True)
                        logging.warn(f"Skip failed. Index too low (Expected: >=1. Recieved: {index + 1})")
                        return

                    elif index > len(player.queue):
                        await ctx.send(f":warning: That index is too high! Queue only {len(player.queue)} items long.", hidden=True)
                        logging.warn(f"Skip failed. Index too high (Expected: <={len(player.queue)}. Recieved: {index + 1}")
                        return

                    else:
                        if trim_queue:
                            logging.info(f"Skipped queue to track {index + 1} of {len(player.queue)}.")
                            del player.queue[:index]
                            next_track = player.queue[0]
                        else:
                            logging.info(f"Jumped to track {index + 1} of {len(player.queue)} in queue.")
                            next_track = player.queue.pop(index)
                            player.queue.insert(0, next_track)


                else:
                    next_track = player.queue[0]
                    logging.info(f"Skipped current track.")

                embed = await self.QM.embed_track(
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
            
        self.QM.update_pages(player)

def setup(bot):
    bot.add_cog(Music(bot))