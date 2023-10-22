import discord
from discord import app_commands
from discord.ext import commands

import config as cfg

from ...handlers.music import MusicHandler
from ...handlers.voice import VoiceHandler
from ...util.models import LavaBot


class Leave(commands.Cog):
    def __init__(self, bot: LavaBot) -> None:
        self.bot = bot
        self.music_handler = MusicHandler(bot)
        self.voice_handler = VoiceHandler(bot)

    @app_commands.command(description="Clears the queue and leaves the call.")
    async def leave(self, inter: discord.Interaction):
        await inter.response.defer()
        player = await self.voice_handler.ensure_voice(inter)

        if not player:
            await inter.followup.send(
                f"{cfg.bot.name} isn't in a call - this won't do anything",
                ephemeral=True,
            )
            return

        await inter.followup.send("Leaving call and clearing queue...")
        await self.voice_handler.cleanup(self.bot, player)

        return


async def setup(bot: LavaBot):
    await bot.add_cog(Leave(bot))
