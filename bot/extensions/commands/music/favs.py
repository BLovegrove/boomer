# core imports
import discord
from discord.ext import commands
from discord import app_commands
import json

# custom imports
from util import Models, MusicHandler, DBHandler, EmbedHandler


class Favs(commands.Cog):

    def __init__(self, bot: Models.LavaBot) -> None:
        self.bot = bot
        self.dbhandler = DBHandler(self.bot.db)
        self.musichandler = MusicHandler(self.bot)

    group = app_commands.Group(
        name="favs", description="Play, edit, and view your favorites list!"
    )

    @group.command(
        name="play",
        description="Play a favorites list! Will look in order of personal > role-based > global depending on whats set",
    )
    async def play(self, itr: discord.Interaction):
        await itr.response.defer()

        list = self.dbhandler.get_favorites(itr.user)
        if not list:
            await itr.followup.send("No favs list found - sorry", ephemeral=True)

        name = list["name"]
        list: dict[str, str] = json.loads(list["entries"])

        for key, value in list.items():
            await self.musichandler.play(itr, value)

        embed = Favs(name, list).construct()

        await itr.followup.send(embed=embed)
        # get info for user id in fav_list
        # if none, try role id
        # if none, go to !DEFAULT
        # if none, complain

    @group.command(
        name="view",
        description="View a favorites list! Pulls the contents of your favorites list without queuing anything",
    )
    async def view(self, itr: discord.Interaction):
        await itr.response.defer()

        list = self.dbhandler.get_favorites(itr.user)
        if not list:
            await itr.followup.send("No favs list found - sorry", ephemeral=True)

        name = list["name"]
        list: dict[str, str] = json.loads(list["entries"])

        embed = EmbedHandler.Favs(name, list).construct()

        await itr.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Favs(bot))
