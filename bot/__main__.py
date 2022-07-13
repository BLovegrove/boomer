import os
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
    
command_folders = [
    'music',
    'admin'
]

module_directory = os.path.join(os.path.dirname(os.path.dirname(__file__))) + '/bot'

def main():
    # laod core cogs
    bot.load_extension('bot.cogs.core.setup')
    bot.load_extension('bot.cogs.core.voice')
    bot.load_extension('bot.cogs.core.queue')
    bot.load_extension('bot.cogs.core.music')
    bot.load_extension('bot.cogs.core.events')
    # dynamically load all the other cogs
    for type in command_folders:
        for file in os.listdir(f'{module_directory}/cogs/{type}'):
            if file.endswith('.py'):
                bot.load_extension(f'bot.cogs.{type}.{file[:-3]}')
                
    cfg = config.load_config()
    
    bot.run(cfg['bot']['token'])

if __name__ == '__main__':
    main()
