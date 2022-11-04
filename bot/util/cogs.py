import logging
import os

from nextcord.ext import commands


def find_all(friendly_names: bool = False):
    logging.debug("STARTED: Scanning and returning all cogs in all subfolders.")

    rootdir = "bot/cogs"
    cogs: list[str] = []

    for subdir, dirs, files in os.walk(rootdir):
        for file in files:
            if file.endswith(".py"):
                module_path = subdir.replace("/", ".")

                logging.debug(
                    f"Subdirectory breadcrumb conversion when scanning cogs: {subdir} to {module_path}"
                )

                if friendly_names:
                    cogs.append(str.capitalize(file[:-3]))

                else:
                    cogs.append(f"{module_path}.{file[:-3]}")

    logging.debug("FINISHED: Scanning and returning all cogs in all subfolders.")
    return cogs


def load_cogs(bot: commands.Bot, cogs: list[str]):
    logging.debug("STARTED: Loading all cogs.")

    bot.load_extensions(cogs)

    logging.debug("FINISHED: Loading all cogs.")
    return
