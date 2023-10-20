import os

from discord.ext import commands


def search() -> list[str]:

    events_list = []

    for folder in os.listdir(f"bot/events/."):
        for filename in os.listdir(f"bot/events/{folder}/."):
            if filename.endswith(".py"):
                events_list.append(f"bot.events.{folder}.{filename[:-3]}")

    return events_list
