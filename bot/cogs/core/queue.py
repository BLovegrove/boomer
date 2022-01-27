# ---------------------------------- Imports --------------------------------- #
import logging
import math
import re
import textwrap

import discord
from discord.ext import commands
from discord_slash import SlashContext
import lavalink
from lavalink import DefaultPlayer, AudioTrack

from ... import config

# ---------------------------------- Config ---------------------------------- #
cfg = config.load_config()
standard_rx = re.compile(r'https?://(?:www\.)?.+')

# --------------------------------- Cog class -------------------------------- #
class QueueManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    # ---------------------------- ANCHOR UPDATE PAGES --------------------------- #
    # Updates the number of pages defined in the config file as queue_page_len 

    def update_pages(self, player: DefaultPlayer):
        player.store('pages', math.ceil(
            len(player.queue) / cfg['music']['queue_page_len']))

    # ----------------------------- ANCHOR EMBED LIST ---------------------------- #
    # Used by the list command to put a queue summary together

    def embed_list(self, player: DefaultPlayer, page: int) -> discord.Embed:
        queue_start = (page - 1) * cfg['music']['queue_page_len']
        queue_end = queue_start + ( cfg['music']['queue_page_len'] - 1) if page < player.fetch('pages') else len(player.queue) - 1
        if queue_end == 0:
            queue_end += 1

        track = player.current

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
            track: AudioTrack = player.queue[i]
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
            text=f"<> for page +/-."
        )

        return embed

    # ---------------------------- ANCHOR EMBED TRACK ---------------------------- #

    async def embed_track(self, ctx: SlashContext, track: AudioTrack, action: str, queue_len: int, footer: str="", author: str="") -> discord.Embed:
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

    # ------------------------------- ANCHOR CLEAR ------------------------------- #
    # Clears either the entire queue if no index is given or a single specific item
    # from the queue.

    async def clear(self, ctx: SlashContext, index: int=0):

        player = await self.VSM.ensure_voice(self, ctx)
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

QM = QueueManager

def setup(bot):
    bot.add_cog(QueueManager(bot))