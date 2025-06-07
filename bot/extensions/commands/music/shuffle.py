# core imports
import discord
from discord.ext import commands
from discord import app_commands

# custom imports
from util import models
from util.handlers.queue import QueueHandler
from util.handlers.voice import VoiceHandler


class Shuffle(commands.Cog):

    def __init__(self, bot: models.LavaBot) -> None:
        self.bot = bot
        self.queuehandler = QueueHandler(self.bot)
        self.voicehandler = VoiceHandler(self.bot)

    @app_commands.command(
        name="shuffle",
        description=f"Toggles queue shuffling",
    )
    # @commands.is_owner() # owner check to lock down access to command
    async def shuffle(self, itr: discord.Interaction):
        await itr.response.defer()

        player = await self.voicehandler.ensure_voice(itr)
        if not player:
            itr.followup.send(
                "Something went wrong while grabbing the player. Pass this on to your server owner or local bot dev."
            )

        shuffled = await self.queuehandler.shuffle(player)
        if shuffled:
            await itr.followup.send("Playing shuffled :twisted_rightwards_arrows:")
        else:
            await itr.followup.send("Playing unshuffled :arrow_right:")


async def setup(bot: models.LavaBot):
    await bot.add_cog(Shuffle(bot))
