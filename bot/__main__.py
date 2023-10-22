import logging
import logging.handlers
import os
import sys
from time import sleep

import discord

try:
    import config as cfg
except:
    os.rename("config.txt", "config.py")
    print(
        "Config file import failed. Please fill out the config file located in /home/boomer/config.py and restart the container."
    )
    while True:
        sleep(60)

from .util.models import LavaBot


# make sure the main py file is being run as a file and not imported
def main():
    bot = LavaBot()
    discord.utils.setup_logging()
    bot.run(cfg.bot.token, log_handler=None)


if __name__ == "__main__":
    main()
