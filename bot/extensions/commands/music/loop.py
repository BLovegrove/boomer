import discord
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands
import lavalink

from util import models
from util.handlers.voice import VoiceHandler


class Loop(commands.Cog):

    def __init__(self, bot: models.LavaBot) -> None:
        self.bot = bot
        self.voice_handler = VoiceHandler(bot)

    @app_commands.command(
        description="Starts looping either the current track, or the entire playlist."
    )
    @app_commands.describe(
        mode="Pick between track and entire playlist to enable repeating on. Clear to turn it off."
    )
    @app_commands.choices(
        mode=[
            Choice(name="track", value="track"),
            Choice(name="playlist", value="playlist"),
            Choice(name="clear", value="clear"),
        ]
    )
    async def loop(self, inter: discord.Interaction, mode: str):
        await inter.response.defer()
        player: lavalink.DefaultPlayer = await self.voice_handler.ensure_voice(inter)

        if not player.is_playing or player.fetch("idle"):
            await inter.followup.send(
                "Idling / Nothing playing at the moment. Try queueing up something first.",
                ephemeral=True,
            )
            return

        match (mode):
            case "track":
                player.set_loop(1)
                await inter.followup.send("Looping on track :repeat_one:")

            case "playlist":
                player.set_loop(2)
                await inter.followup.send("Looping on playlist :repeat:")

            case "clear":
                player.set_loop(0)
                await inter.followup.send("Looping disabled.")

        return


async def setup(bot: models.LavaBot):
    await bot.add_cog(Loop(bot))
