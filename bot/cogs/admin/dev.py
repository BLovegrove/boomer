import discord
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands
from loguru import logger

import config as cfg

from ...handlers.queue import QueueHandler
from ...handlers.voice import VoiceHandler
from ...util.models import LavaBot


class Dev(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: LavaBot = bot

    @app_commands.command(
        name="dev",
        description=f"Runs a series of dev commands for testing and maintenance purposes.",
    )
    @app_commands.choices(
        command=[
            Choice(name="Kill bot", value="die"),
            Choice(name="Ping test", value="ping"),
            Choice(name="Fetch player object", value="fetchplayer"),
            Choice(name="Player queue filler", value="queuespam"),
        ]
    )
    async def dev(self, interaction: discord.Interaction, command: Choice[str]):
        match command.value:
            case "die":
                await interaction.response.send_message(
                    f"Restarting the bot. Please wait until {cfg.bot.name} has the 'Online' or 'Idle' status icon before doing any more commands."
                )
                player = self.bot.lavalink.player_manager.get(interaction.guild_id)
                if player:
                    voice_handler = VoiceHandler(self.bot)
                    await voice_handler.disconnect(self.bot, player)
                await self.bot.close()
                return
            case "ping":
                await interaction.response.send_message(
                    f"Pong! ({self.bot.ws.VOICE_PING})"
                )
                return
            case "fetchplayer":
                await interaction.response.defer(ephemeral=True)
                voice_handler = VoiceHandler(self.bot)
                player = voice_handler.fetch_player(self.bot)
                logger.debug(f"Player: {player}")
                logger.debug(f"Player guild: {player.guild_id}")
                logger.debug(f"Player VC: {player.channel_id}")
                await interaction.edit_original_response(
                    content="Dev command complete."
                )
                return
            case "queuespam":
                await interaction.response.defer(ephemeral=True)
                voice_handler = VoiceHandler(self.bot)
                player = voice_handler.fetch_player(self.bot)
                logger.debug(
                    "Spamming tons of entires to fill up the queue. Give this a sec..."
                )
                songs = [
                    "https://www.youtube.com/watch?v=YnwfTHpnGLY",
                    "https://www.youtube.com/watch?v=tKi9Z-f6qX4",
                    "https://www.youtube.com/watch?v=B7xai5u_tnk",
                    "https://www.youtube.com/watch?v=n8X9_MgEdCg",
                    "https://www.youtube.com/watch?v=CqnU_sJ8V-E",
                ]

                for i in range(5):
                    for song in songs:
                        result = await player.node.get_tracks(song)
                        if result.load_type != result.load_type.TRACK:
                            continue
                        else:
                            player.add(result.tracks[0])

                logger.debug("Finished spamming queue entries.")
                player.store("idle", False)
                player.set_loop(player.LOOP_NONE)
                await player.play()
                queue_handler = QueueHandler(self.bot, voice_handler)
                queue_handler.update_pages(player)
                await interaction.followup.send("Dev command complete.", ephemeral=True)

                return
            case "default":
                await interaction.response.send_message(
                    "Dev comamnd failed. Couldn't find a subcommand matching your input.",
                    ephemeral=True,
                )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Dev(bot))
