# ---------------------------------- Imports --------------------------------- #
import discord
from discord.ext import commands
import lavalink

from ... import config

# ---------------------------------- Config ---------------------------------- #
cfg = config.load_config()

# --------------------------------- Cog class -------------------------------- #
class Setup(commands.Cog):
    def __init__(self, bot):
        self.bot: discord.Client = bot
        
        # Default idle status message to show in discord app
        self.activity_idle = discord.Streaming(name="nothing.", url="https://tinyurl.com/lamzterms")
            
        # Lavalink node connection to running Lavalink.jar server
        bot.lavalink = lavalink.Client(cfg['bot']['id'])
        # Host, Port, Password, Region, Name
        cfg_lava = cfg['lavalink']
        bot.lavalink.add_node(
            host=cfg_lava['ip'], 
            port=cfg_lava['port'], 
            password=cfg_lava['pwd'], 
            region=cfg_lava['region'], 
            reconnect_attempts=-1
        )
        bot.add_listener(bot.lavalink.voice_update_handler,'on_socket_response')

    # ---------------------------------------------------------------------------- #
    #                              Methods / Commands                              #
    # ---------------------------------------------------------------------------- #
    

def setup(bot):
    bot.add_cog(Setup(bot))
