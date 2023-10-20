import os

import mafic
from nextcord.ext import commands

import config as cfg


class MaficBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.pool = mafic.NodePool(self)
        self.loop.create_task(self.add_nodes())

    async def add_nodes(self):
        await self.pool.create_node(
            host=cfg.lavalink.host,
            port=cfg.lavalink.port,
            password=cfg.lavalink.password,
            label=cfg.lavalink.label,
        )


# make sure the main py file is being run as a file and not imported
def main():
    bot = MaficBot(default_guild_ids=[cfg.guild.id])

    # register all cogs
    for folder in os.listdir("bot/cogs"):
        for filename in os.listdir(f"bot/cogs/{folder}"):
            if filename.endswith(".py"):
                bot.load_extension(f"bot.cogs.{folder}.{filename[:-3]}")

    # create mafic node pool

    bot.run(cfg.bot.token)


if __name__ == "__main__":
    main()
