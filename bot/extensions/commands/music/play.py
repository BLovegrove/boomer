import discord
from discord import app_commands
from discord.ext import commands
import lavalink
from loguru import logger

import util.cfg as cfg

from util import models
from util.handlers.music import MusicHandler
from util.handlers.voice import VoiceHandler
from util.handlers.embed import EmbedHandler
from util.handlers.queue import QueueHandler


class Play(commands.Cog):

    def __init__(self, bot: models.LavaBot) -> None:
        self.bot = bot
        self.musichandler = MusicHandler(self.bot)
        self.voicehandler = VoiceHandler(self.bot)
        self.queuehandler = QueueHandler(self.bot)

    @app_commands.command(
        name="play",
        description=f"Plays music! Summons {cfg.bot.name} if they aren't running, adds a song to the queue if they are.",
    )
    @app_commands.describe(search="The name/artist/url of the song you want to find")
    async def play(self, itr: discord.Interaction, search: str = None):
        await itr.response.defer()

        response = await self.voicehandler.ensure_voice(itr)
        if not response.player:
            await itr.followup.send(response.message)
            return
        else:
            player = response.player

        if search:
            queue_start = len(player.queue)
            result = await self.musichandler.play(player, search)
            if len(result.tracks) == 1:
                embed = EmbedHandler.Track(itr, result.tracks[0], player)
            else:
                embed = EmbedHandler.Playlist(
                    itr, result.tracks, result.title, player, queue_start
                )

            await itr.followup.send(embed=embed.construct())
            return

        self.queuehandler.update_pages(player)

        if (player and not player.paused) or not player:
            await itr.followup.send(
                "Nothing is paused - try entering a YouTube or Soundcloud URL to play a new track instead.",
                ephemeral=True,
            )
            return

        await player.set_pause(False)
        logger.info("Player resumed")
        await itr.followup.send("Track resumed :arrow_forward:")

        return


async def setup(bot: models.LavaBot):
    await bot.add_cog(Play(bot))
