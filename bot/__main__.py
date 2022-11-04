import logging
import sys

from colorama import init
from nextcord import Intents
from nextcord.ext import commands

import config as cfg

from .util import helper

init(strip=not sys.stdout.isatty())  # strip colors if stdout is redirected
from pyfiglet import figlet_format
from termcolor import cprint

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=cfg.log_level,
)


def main():

    cprint(
        figlet_format(f"{cfg.bot.name.upper()} START!"), color="magenta", attrs=["bold"]
    )

    bot = commands.Bot(intents=Intents.all())

    @bot.event
    async def on_ready():
        logging.info(f"Logged in as {bot.user}")

        logging.info("Loading cogs...")
        cogs = helper.cogs.find_all()
        helper.cogs.load_cogs(bot, cogs)

        logging.info("Syncing application commands...")
        await bot.sync_all_application_commands()

    bot.run(cfg.bot.token)


if __name__ == "__main__":
    main()
