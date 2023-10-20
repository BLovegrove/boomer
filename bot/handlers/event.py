import os

import discord
import lavalink

from ..util.models import LavaBot


class EventHandler:
    def __init__(self) -> None:
        pass

    def load(self) -> list[str]:
        events_list = []

        for folder in os.listdir(f"bot/events/"):
            for filename in os.listdir(f"bot/events/{folder}/."):
                if filename.endswith(".py"):
                    events_list.append(f"bot.events.{folder}.{filename[:-3]}")

        return events_list
