import discord
from discord import app_commands
from discord.ext import commands

from ...handlers.music import MusicHandler
from ...handlers.queue import QueueHandler
from ...handlers.voice import VoiceHandler
from ...util.models import LavaBot


class Clear(commands.Cog):
    def __init__(self, bot: LavaBot) -> None:
        self.bot = bot
        self.music_handler = MusicHandler(bot)
        self.voice_handler = VoiceHandler(bot)
        self.queue_handler = QueueHandler(bot, self.voice_handler)

    @app_commands.command(description="Clears the whole (or part of the) queue")
    async def clear(self, inter: discord.Interaction, index: int | None):
        await inter.response.defer()
        if not index:
            await self.queue_handler.clear(inter)
            return

        else:
            player = self.voice_handler.fetch_player(self.bot)
            if not player:
                return

            if index <= 0:
                await inter.followup.send(
                    ":warning: That index is too low! Queue starts at #1.",
                    ephemeral=True,
                )

            elif index > len(player.queue):

                await inter.followup.send(
                    f":warning: That index is too high! Queue only {len(player.queue)} items long.",
                    ephemeral=True,
                )

            else:
                await self.queue_handler.clear(inter, index)

        return


async def setup(bot: LavaBot):
    await bot.add_cog(Clear(bot))
