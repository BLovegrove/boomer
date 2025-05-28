import os
import discord
from dotenv import load_dotenv


env = load_dotenv(os.path.join(os.getcwd(), ".env"))

log_level = os.getenv("LOG_LEVEL", "INFO").upper()
if log_level not in ["DEBUG", "INFO", "WARNING", "ERROR"]:
    print(
        "❌ LOG LEVEL IN CONFIG FILE NOT VALID. PLEASE USE ON OF THE OPTIONS SUPPLIED IN THE TEMPLATE. DEFAULTING TO 'INFO' ❌"
    )
    log_level = "INFO"

save_log = os.getenv("SAVE_LOG", "0").lower() in ("true", "1", "t", "y")


# bot-related variables
class bot:
    token = os.getenv("BOT_TOKEN")
    name = os.getenv("BOT_NAME", "Boomer")
    guild_id = int(os.getenv("BOT_GUILD_ID", "0"))
    accent_color = discord.Color.from_str("#" + os.getenv("BOT_ACCENTCOLOR", "eba4be"))


# database schema/connection info
class lavalink:
    host = os.getenv("LL_HOST")
    port = int(os.getenv("LL_PORT"))
    label = os.getenv("LL_LABEL")
    password = os.getenv("LL_PASSWORD")
    region = os.getenv("LL_REGION", "NZ")


class player:
    volume_default = int(os.getenv("PLAYER_VOLUMEDEFAULT", "33"))
    volume_idle = int(os.getenv("PLAYER_VOLUMEIDLE", "5"))
    loading_emoji = os.getenv("PLAYER_LOADINGEMOJI")
