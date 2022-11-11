import logging
import sys

import lavalink
import nextcord
from colorama import init
from nextcord import Intents
from nextcord.ext import commands
from pyfiglet import figlet_format
from termcolor import cprint

from .. import helper

init(strip=not sys.stdout.isatty())  # strip colors if stdout is redirected

import config as cfg

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=cfg.log_level,
)


class LavaBotClient(commands.Bot):
    def __init__(self, intents: nextcord.Intents) -> None:
        super().__init__(intents=intents)
        self.lavalink: lavalink.Client = None

        cprint(
            figlet_format(f"{cfg.bot.name.upper()} START!"),
            color="magenta",
            attrs=["bold"],
        )

    async def on_ready(self):
        logging.info(f"Logged in as {self.user}")

        logging.info("Loading cogs...")
        cogs = helper.cogs.find_all()
        helper.cogs.load_cogs(self, cogs)

        logging.info("Syncing application commands...")
        await self.sync_all_application_commands()
