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
from util.handlers.queue import QueueHandler


class BGM(commands.Cog):

    def __init__(self, bot: models.LavaBot) -> None:
        self.bot = bot
        self.voicehandler = VoiceHandler(self.bot)
        self.queuehandler = QueueHandler(self.bot)
        self.dbhandler = DatabaseHandler(self.bot.db)

    @app_commands.command(
        name="bgm",
        description=f"Updates the default background music.",
    )
    @app_commands.describe(link="Either a SoundCloud (preferred) or Youtube URL.")
    # @commands.is_owner() # owner check to lock down access to command
    @commands.has_any_role([cfg.role.heirarchy[0], cfg.role.heirarchy[1]])
    async def bgm(self, itr: discord.Interaction, link: str):
        await itr.response.defer()
        if re.match(
            r"^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube(?:-nocookie)?\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|live\/|v\/)?)([\w\-]+)(\S+)?$",
            link,
        ) or re.match(
            r"^https?:\/\/(?:soundcloud\.com|snd\.sc)(?:\/\w+(?:-\w+)*)+$", link
        ):
            response = await self.voicehandler.ensure_voice(itr)
            if not response.player:
                await itr.followup.send(response.message)
                return
            else:
                player = response.player

            result = await player.node.get_tracks(link)

            if result.load_type == lavalink.LoadType.TRACK:
                title = result.tracks[0].title
                self.dbhandler.set_bgm(itr.user, link)
                if player.fetch("idle"):
                    player.queue.insert(0, result.tracks[0])
                    player.current = result.tracks[0]
                    await player.play()
                    self.queuehandler.update_pages(player)

                await itr.followup.send(
                    f":musical_note: Background music updated! new track: [{title}]({result.tracks[0].uri})"
                )
                return

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
