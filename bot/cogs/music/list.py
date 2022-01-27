# ---------------------------------- Imports --------------------------------- #
import logging

import discord
from discord.ext import commands
import discord_slash
from discord_slash import SlashContext, cog_ext
from discord_slash.utils.manage_commands import create_option
from discord_slash.utils.manage_components import create_button, create_actionrow

from ... import config
from ..core.voice import VoiceStateManager as VSM
from ..core.queue import QueueManager as QM

# ---------------------------------- Config ---------------------------------- #
cfg = config.load_config()

# --------------------------------- Cog class -------------------------------- #
class List(commands.Cog):
    def __init__(self, bot):
        self.bot: discord.Client = bot
        self.VSM: VSM = bot.get_cog('VoiceStateManager')
        self.QM: QM = bot.get_cog('QueueManager')

    # ---------------------------------------------------------------------------- #
    #                              Methods / Commands                              #
    # ---------------------------------------------------------------------------- #

    # -------------------------------- ANCHOR LIST ------------------------------- #
    # Displays whole queue in an embed. Also leverages slash components to enable interaction. 
    # Skip pages / clear items / skip to particular tracks without using more commands. 

    @cog_ext.cog_slash(
        name="list",
        description="Displays an interactive list of songs in the queue",
        guild_ids=cfg['guild_ids'],
        options=[
            create_option(
                name="page",
                description="Create list on a specific page from 1 to <max pages> (check /list if you arent sure).",
                option_type=int,
                required=False
            )
        ]
    )
    async def list(self, ctx: SlashContext, page: int=1):
        player = await self.VSM.ensure_voice(ctx)
        if not player:
            return
        else:
            logging.info(f"[{ctx.author.name}" + (f"#{ctx.author.discriminator}" if ctx.author.discriminator else "#0000") + f"] Fetching queue list...")
                
        pages = player.fetch('pages')
        if page > pages:
            if pages > 0:
                await ctx.send(f"Page #{page} too high. Queue is only {pages} pages long.")
            else:
                await ctx.send("Queue is empty - no list to show.")
            return

        components = []

        list_buttons = [
            create_button(
                style=discord_slash.ButtonStyle.primary,
                label="<",
                custom_id="list_page_prev"
            ),
            create_button(
                style=discord_slash.ButtonStyle.primary,
                label=">",
                custom_id="list_page_next"
            )
        ]

        button_row = create_actionrow(*list_buttons)
        components.append(button_row)

        embed = self.QM.embed_list(player, page)
        message = await ctx.send(embed=embed, components=components)
        await message.edit(content=message.content)

def setup(bot):
    bot.add_cog(List(bot))