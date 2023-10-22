import discord
import lavalink

from ..util.models import LavaBot


class PresenceHandler:
    def __init__(self) -> None:
        pass

    @staticmethod
    async def update_status(bot: LavaBot, player: lavalink.DefaultPlayer = None):
        suffix = ""

        if player and player.fetch("track_repeat"):
            suffix = " (on repeat)"

        activity = None
        status = None

        if player and player.is_playing and not player.fetch("idle"):
            activity = discord.Activity(
                name=f"{player.current.title + suffix}",
                type=discord.ActivityType.listening,
            )
            status = discord.Status.online
        else:
            activity = discord.Activity(
                name="nothing.", type=discord.ActivityType.listening
            )
            status = discord.Status.idle

        await bot.change_presence(activity=activity, status=status)
        return
