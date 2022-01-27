# ---------------------------------- Imports --------------------------------- #
import logging

import discord
from discord.ext import commands
from discord_slash import SlashContext, cog_ext
from discord_slash.model import SlashCommandPermissionType
from discord_slash.utils.manage_commands import create_permission
from lavalink import DefaultPlayer

from ... import config
from ..core.voice import VoiceStateManager as VSM

# ---------------------------------- Config ---------------------------------- #
cfg = config.load_config()

# --------------------------------- Cog class -------------------------------- #
class Die(commands.Cog):
    def __init__(self, bot):
        self.bot: discord.Client = bot
        self.VSM: VSM = bot.get_cog('VoiceStateManager')

    # ---------------------------------------------------------------------------- #
    #                              Methods / Commands                              #
    # ---------------------------------------------------------------------------- #

    # -------------------------------- ANCHOR DIE -------------------------------- #
    # Also disconnects him and clears queue.

    @cog_ext.cog_slash(
        name="die",
        description="Disconnects and shuts down Boomer safely",
        guild_ids=cfg['guild_ids'],
        default_permission=False,
        permissions={
            cfg['guild_ids'][0]: [
                create_permission(cfg['owner_id'], SlashCommandPermissionType.USER, True)
            ]
        }
    )
    async def _die(self, ctx: SlashContext):
        player = await self.VSM.ensure_voice(ctx)

        if player:
            player.queue.clear()
            await player.stop()
            await ctx.guild.change_voice_state(channel=None)

        await self.VSM.update_status(player)
        await ctx.send(f"My battery is low and it's getting dark :(")
        logging.info(f"[{ctx.author.name}" + (f"#{ctx.author.discriminator}" if ctx.author.discriminator else "#0000") + f"] Killed boomer.")
        await ctx.bot.close()
        return

def setup(bot):
    bot.add_cog(Die(bot))