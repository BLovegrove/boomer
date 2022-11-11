from nextcord import Intents

import config as cfg

from .util.models.client import LavaBotClient


def main():

    client = LavaBotClient(Intents.all())

    client.run(cfg.bot.token)


if __name__ == "__main__":
    main()
