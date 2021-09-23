from discord.ext import commands
from discord_slash.client import SlashCommand
from . import config

cfg = config.load_config()

bot = commands.Bot(command_prefix="!")
slash = SlashCommand(bot, sync_commands=True)


@bot.event
async def on_ready():
    print(f'{bot.user} has logged in.')

def main():
    bot.load_extension('bot.cogs.music')
    bot.run(cfg['token'])

if __name__ == '__main__':
    main()
