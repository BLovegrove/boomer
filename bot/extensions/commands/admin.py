# core imports
import discord
from discord.ext import commands
from discord import app_commands
from discord.app_commands import Choice

# custom imports
from util import models
import util.config as cfg


class Admin(commands.Cog):
    def __init__(self, bot: models.LavaBot) -> None:
        self.bot = bot

    @app_commands.command(
        name="admin",
        description=f"Runs a series of dev commands for testing and maintenance purposes.",
    )
    @app_commands.choices(
        command=[
            Choice(name="Kill bot", value="die"),
            Choice(name="Ping test", value="ping"),
        ]
    )
    @commands.is_owner()
    async def admin(self, itr: discord.Interaction, command: Choice[str]):
        match command.value:
            case "die":
                await itr.response.send_message(
                    f"Restarting the bot. Please wait until {cfg.bot.name} has the 'Online' or 'Idle' status icon before doing any more commands.",
                    ephemeral=True,
                )
                await self.bot.change_presence(status=discord.Status.offline)
                await self.bot.lavalink.close()
                await self.bot.close()
                return

            case "ping":
                await itr.response.send_message(
                    f"Pong! Here are the round trip times: \n"
                    + f"Bot: {round(self.bot.latency * 1000)}ms",
                    ephemeral=True,
                )
                return

            case "default":
                await itr.response.send_message(
                    "Dev comamnd failed. Couldn't find a subcommand matching your input.",
                    ephemeral=True,
                )


async def setup(bot):
    await bot.add_cog(Admin(bot))
