import discord
from discord import app_commands
from discord.ext import commands

from util import models
from util.handlers.music import MusicHandler
from util.handlers.queue import QueueHandler
from util.handlers.voice import VoiceHandler
from util.handlers.embed import EmbedHandler


class Clear(commands.Cog):

    def __init__(self, bot: models.LavaBot) -> None:
        self.bot = bot
        self.musichandler = MusicHandler(bot)
        self.voicehandler = VoiceHandler(bot)
        self.queuehandler = QueueHandler(bot)

    @app_commands.command(description="Clears the whole (or part of the) queue")
    async def clear(self, itr: discord.Interaction, index: int | None):
        await itr.response.defer()

        player = self.voicehandler.fetch_player(self.bot)
        if not player:
            await itr.followup.send(
                ":warning: Nothing playing right now - there's nothing to clear.",
                ephemeral=True,
            )
            return

        if not index:
            await self.queuehandler.clear(player)
            return

        if index <= 0:
            await itr.followup.send(
                ":warning: That index is too low! Queue starts at #1.",
                ephemeral=True,
            )

        elif index > len(player.queue):
            await itr.followup.send(
                f":warning: That index is too high! Queue only {len(player.queue)} items long.",
                ephemeral=True,
            )

        else:
            result = await self.queuehandler.clear(player, index)
            if not result:
                await itr.followup.send(
                    "Something went wrogn while clearing the queue. Please contact your server owner or local dev.",
                    ephemeral=True,
                )

            if result.cleared:
                embed = EmbedHandler.Cleared(itr, result.cleared, player, result.index)
                await itr.followup.send(embed=embed.construct())
            else:
                itr.followup.send(":boom: Queue cleared!")


async def setup(bot: models.LavaBot):
    await bot.add_cog(Clear(bot))
