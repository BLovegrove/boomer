import os

from discord.ext import commands


def search() -> list[str]:

    cogs_list = []

    for folder in os.listdir(f"bot/cogs/."):
        for filename in os.listdir(f"bot/cogs/{folder}/."):
            if filename.endswith(".py"):
                cogs_list.append(f"bot.cogs.{folder}.{filename[:-3]}")

    return cogs_list
