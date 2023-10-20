import mafic
import nextcord
from nextcord.ext import commands


class Pause(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot = bot

    @nextcord.slash_command(name="pause")
    async def pause(self, inter: nextcord.Interaction):
        await inter.response.defer()

        if not inter.guild.voice_client:
            player = await inter.user.voice.channel.connect(cls=mafic.Player)
        else:
            player = inter.guild.voice_client

        await player.pause()
        await inter.send("Paused.")


def setup(bot: commands.Bot):
    bot.add_cog(Pause(bot))
