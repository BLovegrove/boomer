from discord.ext import commands
import discord
import toml
from datetime import datetime
from .. import util


class Meta(commands.Cog):
    """Commands relating to the bot itself."""

    def __init__(self, bot):
        self.bot = bot
        self.start_time = datetime.now()
        config = toml.load("./config.toml")
        self.config = config

    @commands.command()
    async def uptime(self, ctx):
        """Tells how long the bot has been running."""
        uptime_seconds = round(
            (datetime.now() - self.start_time).total_seconds())
        await ctx.send(f"Current Uptime: {util.format_seconds(uptime_seconds)}"
                       )

def setup(bot):
    bot.add_cog(Meta(bot))
