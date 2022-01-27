# ---------------------------------- Imports --------------------------------- #
import logging

import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
import lavalink

from ... import config
from ..core.voice import VoiceStateManager as VSM
from ..core.music import Music
from ..core.events import Events

# ---------------------------------- Config ---------------------------------- #
cfg = config.load_config()

# --------------------------------- Cog class -------------------------------- #
class Shortcuts(commands.Cog):
    def __init__(self, bot):
        self.bot: discord.Client = bot
        self.VSM: VSM = bot.get_cog('VoiceStateManager')
        self.Music: Music = bot.get_cog('Music')
        self.events: Events = bot.get_cog('Events')

    # ---------------------------------------------------------------------------- #
    #                              Methods / Commands                              #
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
        player = await self.VSM.ensure_voice(ctx)
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
            await self.events.hooks(lavalink.QueueEndEvent(player))
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
        player = await self.VSM.ensure_voice(ctx)
        if not player:
            return
        else:
            logging.info(f"[{ctx.author.name}" + (f"#{ctx.author.discriminator}" if ctx.author.discriminator else "#0000") + f"] Playing lofi radio...")

        query = "https://www.youtube.com/watch?v=5qap5aO4i9A"
        await self.Music.play(ctx, query)


def setup(bot):
    bot.add_cog(Shortcuts(bot))
