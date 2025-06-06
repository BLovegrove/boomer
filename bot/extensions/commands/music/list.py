import discord
import lavalink
from discord import app_commands
from discord.ext import commands
from loguru import logger

from util import models
from util.handlers.embed import EmbedHandler
from util.handlers.music import MusicHandler
from util.handlers.voice import VoiceHandler


class PaginationButtons(discord.ui.View):
    def __init__(
        self,
        list_interaction: discord.Interaction,
        player: lavalink.DefaultPlayer,
        page: int,
    ):
        super().__init__(timeout=None)
        self.page = page
        self.player = player
        self.list = list_interaction

    def check_boundaries(self):
        if self.page <= 1:
            self.button_prev.disabled = True
        else:
            self.button_prev.disabled = False

        if self.page >= self.player.fetch("pages"):
            self.button_next.disabled = True
        else:
            self.button_next.disabled = False

        logger.debug(
            f"Button states: < {self.button_prev.disabled} > {self.button_next.disabled}"
        )

        return

    @discord.ui.button(
        label="<", custom_id="page_prev", style=discord.ButtonStyle.blurple
    )
    async def button_prev(self, inter: discord.Interaction, button: discord.ui.Button):
        embed = EmbedHandler.List(self.player, self.page - 1).construct()
        self.page -= 1
        self.check_boundaries()
        await inter.response.edit_message(view=self)
        await self.list.edit_original_response(embed=embed)

    @discord.ui.button(
        label=">", custom_id="page_next", style=discord.ButtonStyle.blurple
    )
    async def button_next(self, inter: discord.Interaction, button: discord.ui.Button):
        embed = EmbedHandler.List(self.player, self.page + 1).construct()
        self.page += 1
        self.check_boundaries()
        await inter.response.edit_message(view=self)
        await self.list.edit_original_response(embed=embed)


class List(commands.Cog):
    def __init__(self, bot: models.LavaBot) -> None:
        self.bot = bot
        self.musichandler = MusicHandler(bot)
        self.voicehandler = VoiceHandler(bot)

    @app_commands.command(
        description="Displays an interactive queue listing! Click the buttons to cycle through pages."
    )
    @app_commands.describe(
        page="Page of the queue you want to list off. If you're unsure, just leave this blank."
    )
    async def list(self, itr: discord.Interaction, page: int = None):
        await itr.response.defer()

        response = await self.voicehandler.ensure_voice(itr)
        if not response.player:
            await itr.followup.send(response.message)
            return
        else:
            player = response.player

        page = page if page != None else 1

        view = PaginationButtons(itr, player, page)

        if page <= 1:
            view.button_prev.disabled = True

        if page >= player.fetch("pages"):
            view.button_next.disabled = True

        embed = EmbedHandler.List(player, page).construct()
        await itr.followup.send(embed=embed, view=view)

        return


async def setup(bot: models.LavaBot):
    await bot.add_cog(List(bot))
