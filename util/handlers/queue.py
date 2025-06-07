import math
import lavalink

from util import models

__all__ = ["QueueHandler"]


class QueueHandler:
    def __init__(self, bot: models.LavaBot) -> None:
        self.bot = bot

    class ClearResult:
        def __init__(self, cleared: lavalink.AudioTrack, index: int):
            self.cleared = cleared
            self.index = index

    def update_pages(self, player: lavalink.DefaultPlayer):
        player.store("pages", max(math.ceil(len(player.queue) / 9), 0))

    async def clear(self, player: lavalink.DefaultPlayer, index: int = None):

        if not index:
            player.queue.clear()
            player.store("pages", 0)
            return self.ClearResult(None, None)

        else:
            cleared = player.queue.pop(index - 1)
            if not cleared:
                return

            return self.ClearResult(cleared, index)

    async def shuffle(self, player: lavalink.DefaultPlayer):

        player.set_shuffle(not player.shuffle)

        return player.shuffle
