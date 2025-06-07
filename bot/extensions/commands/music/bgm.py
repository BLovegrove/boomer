# core imports
import discord
from discord.ext import commands
from discord import app_commands
import re

import lavalink

# custom imports
from util import cfg, models
from util.handlers.database import DatabaseHandler
from util.handlers.voice import VoiceHandler
from util.handlers.music import MusicHandler


class BGM(commands.Cog):

    def __init__(self, bot: models.LavaBot) -> None:
        self.bot = bot
        self.voicehandler = VoiceHandler(self.bot)
        self.musichandler = MusicHandler(self.bot)
        self.dbhandler = DatabaseHandler(self.bot.db)

    @app_commands.command(
        name="bgm",
        description=f"Updates the default background music.",
    )
    @app_commands.describe(link="Either a SoundCloud (preferred) or Youtube URL.")
    # @commands.is_owner() # owner check to lock down access to command
    @commands.has_any_role([cfg.role.heirarchy[0], cfg.role.heirarchy[1]])
    async def bgm(self, itr: discord.Interaction, link: str):
        if re.match(
            r"^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube(?:-nocookie)?\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|live\/|v\/)?)([\w\-]+)(\S+)?$",
            link,
        ) or re.match(
            r"^https?:\/\/(?:soundcloud\.com|snd\.sc)(?:\/\w+(?:-\w+)*)+$", link
        ):
            if len(self.bot.lavalink.player_manager.find_all()) == 0:
                player: lavalink.DefaultPlayer = (
                    self.bot.lavalink.player_manager.create(itr.guild.id)
                )
            else:
                player: lavalink.DefaultPlayer = self.bot.lavalink.player_manager.get(
                    itr.guild.id
                )

            result = await player.node.get_tracks(link)

            if result.load_type == lavalink.LoadType.TRACK:
                title = result.tracks[0].title
                self.dbhandler.set_bgm(itr.user, link)
                await itr.response.send_message(f"Updated BGM to: {title}")

            else:
                await itr.response.send_message(
                    "BGM failed to load. You either used a playlist, or an invalid link. Must be a single track",
                    ephemeral=True,
                )

        else:
            await itr.response.send_message(
                "BGM failed to load. You didn't enter a valid SoundCloud URL/Youtube URL",
                ephemeral=True,
            )


async def setup(bot: models.LavaBot):
    await bot.add_cog(BGM(bot))
