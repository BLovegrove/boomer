import nextcord
from nextcord.ext import commands


class Ping(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot = bot

    @nextcord.slash_command(name="ping")
    async def _ping(self, inter: nextcord.Interaction):
        await inter.response.send_message(
            f"Pong! ({round(self.bot.latency * 1000)} ms)"
        )


def setup(bot: commands.Bot):
    bot.add_cog(Ping(bot))
