import discord
from discord.enums import Status
from discord.ext import commands
from discord_slash.client import SlashCommand
from . import config
import logging

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)

bot = commands.Bot(
    command_prefix="!wat", 
    activity=discord.Game(name="nothing."), 
    status=Status.idle
)
slash = SlashCommand(bot, sync_commands=True)

@bot.event
async def on_ready():
    logging.info(f'{bot.user} has logged in.')


def main():
    bot.load_extension('bot.cogs.music')
    cfg = config.load_config()
    bot.run(cfg['bot']['token'])

if __name__ == '__main__':
    main()
