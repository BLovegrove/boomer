# core imports
import json
import discord
from discord.ext import commands
from discord import app_commands
import lavalink
from loguru import logger

# custom imports
from util import models
from util.handlers.music import MusicHandler
from util.handlers.voice import VoiceHandler
from util.handlers.embed import EmbedHandler
from util.handlers.database import DatabaseHandler


class Favs(commands.Cog):

    def __init__(self, bot: models.LavaBot) -> None:
        self.bot = bot
        self.dbhandler = DatabaseHandler(self.bot.db)
        self.musichandler = MusicHandler(self.bot)
        self.voicehandler = VoiceHandler(self.bot)

    group = app_commands.Group(
        name="favs", description="Play, edit, and view your favorites!"
    )

    @group.command(
        name="play",
        description="Play a favorite songs! Will look in order of personal > role-based > global depending on whats set",
    )
    async def play(self, itr: discord.Interaction):
        await itr.response.defer()

        response = await self.voicehandler.ensure_voice(itr)
        if not response.player:
            await itr.followup.send(response.message)
            return
        else:
            player = response.player

        favs = self.dbhandler.get_favorites(itr.user)
        if not favs:
            await itr.followup.send("No favs list found - sorry", ephemeral=True)
            return

        list_decoded: dict = json.loads(favs["entries"])
        list_links = list(list_decoded.values())

        queue_start = len(player.queue)

        result = await self.musichandler.play(player, list_links)
        embed = EmbedHandler.Playlist(
            itr, result.tracks, favs["name"], player, queue_start
        )

        await itr.followup.send(embed=embed.construct())

    @group.command(
        name="view",
        description="View a favorites list! Pulls the contents of your favorites list without queuing anything",
    )
    async def view(self, itr: discord.Interaction):
        await itr.response.defer()

        list = self.dbhandler.get_favorites(itr.user)
        if not list:
            await itr.followup.send("No favs list found - sorry", ephemeral=True)
            return

        embed = EmbedHandler.Favs(self.bot, list)

        await itr.followup.send(embed=embed.construct())


async def setup(bot: models.LavaBot):
    await bot.add_cog(Favs(bot))
