import discord
import logging
import sys
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from .cogs import music, error, meta
from . import config

cfg = config.load_config()

bot = commands.Bot(command_prefix=cfg["prefix"])
slash = SlashCommand(bot, sync_commands=True)

@bot.event
async def on_ready():
    logging.info(f"Logged in as {bot.user.name}")

COGS = [music.Music, error.CommandErrorHandler, meta.Meta]
EXTS = ["bot.cogs.music"]

def load_exts(bot):
    for ext in EXTS:
        bot.load_extension(ext)

# def add_cogs(bot):
#     for cog in COGS:
#         bot.add_cog(cog(bot, cfg))  # Initialize the cog and add it to the bot

def run():
    load_exts(bot)
    # add_cogs(bot)
    if cfg["token"] == "":
        raise ValueError(
            "No token has been provided. Please ensure that config.toml contains the bot token."
        )
    
    bot.run(cfg["token"])
