import math
import discord
import lavalink

from util import EmbedHandler, VoiceHandler, Models

__all__ = []


class QueueHandler:
    def __init__(self, bot: Models.LavaBot, voice_handler: VoiceHandler) -> None:
        self.bot = bot
        self.voice_handler = voice_handler

    def update_pages(self, player: lavalink.DefaultPlayer):
        player.store("pages", math.ceil(len(player.queue) / 9))

    async def clear(self, itr: discord.Interaction, index: int = None):
        player = await self.voice_handler.ensure_voice(itr)

        if not index:
            player.queue.clear()
            player.store("pages", 0)
            await itr.followup.send(":boom: Queue cleared!")

        else:
            cleared = player.queue.pop(index - 1)

            if not cleared:
                await itr.followup.send(
                    f"Failed to clear track: Track at index {index} not found. Index must be between 1 and {len(player.queue)}"
                )

            embed = EmbedHandler.Cleared(itr, cleared, player, index).construct()
            await itr.followup.send(embed=embed)
