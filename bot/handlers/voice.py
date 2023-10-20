import discord
import lavalink
from loguru import logger

import config as cfg

from ..handlers.presence import PresenceHandler
from ..util.models import LavaBot, LavalinkVoiceClient


class VoiceHandler:
    def __init__(self, bot: LavaBot) -> None:
        self.bot = bot

    def fetch_player(self, bot: LavaBot) -> lavalink.DefaultPlayer:
        player = bot.lavalink.player_manager.get(cfg.guild.id)
        return player

    async def ensure_voice(self, interaction: discord.Interaction):
        """This check ensures that the bot and command author are in the same voicechannel."""
        player: lavalink.DefaultPlayer = self.bot.lavalink.player_manager.create(
            interaction.guild.id
        )
        # Create returns a player if one exists, otherwise creates.
        # This line is important because it ensures that a player always exists for a guild.

        # Most people might consider this a waste of resources for guilds that aren't playing, but this is
        # the easiest and simplest way of ensuring players are created.

        # These are commands that require the bot to join a voicechannel (i.e. initiating playback).
        # Commands such as volume/skip etc don't require the bot to be in a voicechannel so don't need listing here.
        should_connect = interaction.command.name in ("play", "join", "favs", "party")

        if not interaction.user.voice or not interaction.user.voice.channel:
            # Our cog_command_error handler catches this and sends it to the voicechannel.
            # Exceptions allow us to "short-circuit" command invocation via checks so the
            # execution state of the command goes no further.
            await interaction.response.send_message("Join a voicechannel first")
            return

        v_client = interaction.guild.voice_client
        if not v_client:
            if not should_connect:
                # raise commands.CommandInvokeError("Not connected.")
                await interaction.response.send_message(
                    f"{cfg.bot.name} not running yet. Try /join or /play first"
                )

            player.store("summoner_id", interaction.user.id)
            await interaction.user.voice.channel.connect(cls=LavalinkVoiceClient)
        else:
            if v_client.channel.id != interaction.user.voice.channel.id:
                await interaction.response.send_message(
                    f"Not connected to my channel. Join <#{player.channel_id}>"
                )

        player.store("last_channel", interaction.channel_id)
        return player

    async def disconnect(self, bot: LavaBot, player: lavalink.DefaultPlayer):
        player.queue.clear()
        await player.stop()
        player.set_repeat(False)
        player.store("track_repeat", False)
        await player.set_volume(cfg.player.volume_default)
        await player.clear_filters()
        await bot.get_guild(player.guild_id).voice_client.disconnect()
        await player.destroy()
        await PresenceHandler.update_status(bot, player)
