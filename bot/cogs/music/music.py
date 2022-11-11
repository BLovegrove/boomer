import logging
import re
import time

import nextcord
import nextwave
from nextcord import slash_command
from nextcord.abc import GuildChannel
from nextcord.ext import commands

import config as cfg

from ...util.models.client import LavaBotClient

lavacfg = cfg.lavalink

url_rx = re.compile(r"https?://(?:www\.)?.+")


class Music(commands.Cog):
    """Music cog to hold Wavelink related commands and listeners."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        bot.loop.create_task(self.connect_nodes())

    async def connect_nodes(self):
        """Connect to our Lavalink nodes."""
        await self.bot.wait_until_ready()

        await nextwave.NodePool.create_node(
            bot=self.bot,
            host=lavacfg.host,
            port=lavacfg.port,
            password=lavacfg.password,
        )

    @commands.Cog.listener()
    async def on_nextwave_node_ready(self, node: nextwave.Node):
        """Event fired when a node has finished connecting."""
        logging.info(f"Node: <{node.identifier}> is ready!")

    async def connect(self, interaction: nextcord.Interaction):
        try:
            channel = interaction.user.voice.channel
        except AttributeError:
            return await interaction.send(
                "No voice channel to connect to. Please either provide one or join one."
            )

        # vc is short for voice client...
        # Our "vc" will be our wavelink.Player as typehinted below...
        # wavelink.Player is also a VoiceProtocol...

        vc: nextwave.Player = await channel.connect(cls=nextwave.Player)
        return vc

    @slash_command(
        description="Play a song with the given search query.",
        guild_ids=[cfg.bot.guild_id],
    )
    async def play(
        self,
        interaction: nextcord.Interaction,
        query: str = nextcord.SlashOption(required=True),
    ):
        # if not interaction.guild.voice_client:
        # vc: wavelink.Player = await interaction.user.voice.channel.connect(
        #     cls=wavelink.Player
        # )
        # else:
        #     vc: wavelink.Player = interaction.guild.voice_client

        vc: nextwave.Player = await self.connect(interaction)
        track = await nextwave.YouTubeTrack.search(query=query, return_first=True)
        await vc.set_filter(
            nextwave.Filter(volume=1.0, timescale=nextwave.Timescale(rate=2.0))
        )
        await vc.play(track)


def setup(bot):
    bot.add_cog(Music(bot))
