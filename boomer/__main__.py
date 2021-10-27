import os
import discord
from discord.enums import Status
from discord.ext import commands
from discord_slash.client import SlashCommand
import argparse
from . import config

parser = argparse.ArgumentParser()
parser.add_argument(
    "-b", 
    "--bot", 
    help="Type of bot to run (0:boomer, 1:zoomer, 2:both)", 
    type=int
)
args = parser.parse_args()

bot = commands.Bot(command_prefix="!wat", activity=discord.Game(name="nothing."), status=Status.idle)
slash = SlashCommand(bot, sync_commands=True)

@bot.event
async def on_ready():
    print(f'{bot.user} has logged in.')

def main():
    bot.load_extension('boomer.cogs.music')
    cfg = config.load_config()
    bot.run(cfg['bot']['token'])

if __name__ == '__main__':
    main()
