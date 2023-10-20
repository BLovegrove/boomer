import mafic
import nextcord
from nextcord.ext import commands


class Play(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__()
        self.bot = bot

    @nextcord.slash_command(name="play")
    async def play(self, inter: nextcord.Interaction, query: str = None):
        await inter.response.defer()

        if not inter.guild.voice_client:
            player = await inter.user.voice.channel.connect(cls=mafic.Player)
        else:
            player = inter.guild.voice_client

        if not query:
            await player.resume()
            await inter.send(f"Resuming track: {player.current.title}")
        else:
            tracks = await player.fetch_tracks(query)

            if not tracks:
                await inter.send("No tracks found.")

            track = tracks[0]

            await player.play(track)
            await inter.send(f"Now playing: {track.title}")


def setup(bot: commands.Bot):
    bot.add_cog(Play(bot))
