import math

import discord
import lavalink
from discord.ext import commands

import config as cfg

from ..handlers import embeds
from ..handlers.voice import VoiceHandler
from ..util import models


class QueueHandler:
    def __init__(self, bot: models.LavaBot, voice_handler: VoiceHandler) -> None:
        self.bot = bot
        self.voice_handler = voice_handler

    def update_pages(self, player: lavalink.DefaultPlayer):
        player.store("pages", math.ceil(len(player.queue) / 9))

    async def clear(self, interaction: discord.Interaction, index: int = None):
        player = await self.voice_handler.ensure_voice(interaction)

        if not index:
            player.queue.clear()
            player.store("pages", 0)
            await interaction.followup.send(":boom: Queue cleared!")

        else:
            cleared = player.queue.pop(index - 1)

            if not cleared:
                await interaction.followup.send(
                    f"Failed to clear track: Track at index {index} not found. Index must be between 1 and {len(player.queue)}"
                )

            embed = embeds.ClearedEmbedBuilder(interaction, cleared, player, index)
            await interaction.followup.send(embed=embed.construct())
