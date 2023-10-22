import discord
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands

from ...handlers.voice import VoiceHandler
from ...util.models import LavaBot


class Loop(commands.Cog):
    def __init__(self, bot: LavaBot) -> None:
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
        player = await self.voice_handler.ensure_voice(inter)

        if not player.is_playing or player.fetch("idle"):
            await inter.followup.send(
                "Idlinng / Nothing playing at the moment. Try queueing up something first.",
                ephemeral=True,
            )
            return

        match (mode):
            case "track":
                player.set_loop(player.LOOP_SINGLE)
                await inter.followup.send("Looping on track :repeat_one:")

            case "playlist":
                player.set_loop(player.LOOP_QUEUE)
                await inter.followup.send("Looping on playlist :repeat:")

            case "clear":
                player.set_loop(player.LOOP_NONE)
                await inter.followup.send("Looping disabled.")

        return


async def setup(bot: LavaBot):
    await bot.add_cog(Loop(bot))
