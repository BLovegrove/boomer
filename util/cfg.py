import os
import discord
from dotenv import load_dotenv

__all__ = ["log_level", "save_log", "bot", "role", "lavalink", "player", "db", "path"]

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


class role:
    heirarchy = os.getenv("ROLE_HEIRARCHY").split(",")


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
    bgm_default = os.getenv(
        "PLAYER_BGMDEFAULT",
        "https://soundcloud.com/closedonsundayy/201016-star-wars-lofi-mix-1-hour?in=8vukqpvbefqi/sets/no1",
    )


class db:
    host = os.getenv("DB_HOST")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    name = os.getenv("DB_NAME")
    pool = os.getenv("POOL_NAME", "bot_pool")

    class table:
        members = "members"
        favs = "fav_lists"
        bgm = "bgm"


# file paths
class path:
    root = os.getenv("PATH_ROOT", "")
    avatars = os.getenv("PATH_AVATARS", "avatars").strip("/")


class image:
    unknown = "https://imgur.com/a/jql8DP5"
    boombox = "https://imgur.com/a/33ed4oY"
