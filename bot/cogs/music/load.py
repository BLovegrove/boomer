# ---------------------------------- Imports --------------------------------- #
import logging

import discord
from discord.ext import commands
from discord_slash import SlashContext, cog_ext
from discord_slash.utils.manage_commands import create_option

from ... import config
from ... import util
from ..core.voice import VoiceStateManager as VSM
from ..core.music import Music
from ..core.queue import QueueManager as QM

# ---------------------------------- Config ---------------------------------- #
cfg = config.load_config()

# --------------------------------- Cog class -------------------------------- #
class Load(commands.Cog):
    def __init__(self, bot):
        self.bot: discord.Client = bot
        self.VSM: VSM = bot.get_cog('VoiceStateManager')
        self.QM: QM = bot.get_cog('QueueManager')
        self.Music: Music = bot.get_cog('Music')

    # ---------------------------------------------------------------------------- #
    #                              Methods / Commands                              #
    # ---------------------------------------------------------------------------- #

    # -------------------------------- ANCHOR LOAD ------------------------------- #
    # Loads a given previously saved queue from disk and overrides the current
    # queue.

    @cog_ext.cog_slash(
        name="load",
        description="Clears current queue and loads requested one by name. (check /favs if you arent sure)",
        guild_ids=cfg['guild_ids'],
        options = [
            create_option(
                name="name",
                description="The title of the previously saved queue you want to load",
                option_type=str,
                required=True
            )
        ]
    )
    async def load(self, ctx: SlashContext, name: str=""):
        player = await self.VSM.ensure_voice(ctx)
        if not player:
            return
        else:
            logging.info(f"[{ctx.author.name}" + (f"#{ctx.author.discriminator}" if ctx.author.discriminator else "#0000") + f"] Fetching saved queue '{name}' from disk...")

        if (name != ""):
            player.queue.clear()

            logging.info("Attempting to load custom saved queue.")
            name = name.lower() # santiy checking case
            master_list = config.load_queues()
            if (name not in master_list.keys()):
                logging.warn(f"Failed to find saved queue by the name '{name}'!")
                await ctx.send(f"Couldn't find a saved queue by the name '{name}'. See /favs for a list of saved queues.")
            else:
                loaded_queue = master_list[name]

                embed = discord.Embed(color=discord.Color.blurple())
                embed.set_author(
                    name=f"Loading saved queue: {name}",
                    url="https://tinyurl.com/boomermusic",
                    icon_url="https://i.imgur.com/dpVBIer.png"
                )
                embed.description = util.progress_bar(
                    0, 
                    len(loaded_queue)
                )
                embed.set_footer(
                    text="Please note: This can take a long time for large queues - sorry!"
                )

                logging.info("Trying to get saved queue. Better get some popcorn while you wait.")
                loading_msg = await ctx.send(embed=embed)
                await loading_msg.edit(embeds=[embed])

                loaded = 0

                for track_url in loaded_queue:

                    try:
                        if (loaded == 0):
                            if (player.fetch('idle')):
                                await self.Music.play(ctx, track_url)
                            else:
                                await self.Music.play(ctx, track_url)
                                await player.skip()

                        else:
                            results = await player.node.get_tracks(f"ytsearch:{track_url}")
                            track = results['tracks'][0]
                            player.add(requester=ctx.author.id, track=track)

                        self.QM.update_pages(player)
                    except:
                        logging.warn(f"Song '{track_url}' could not be found! Skipping...")
                        
                    loaded += 1

                    if (loaded % 1 == 0):
                        embed.description = util.progress_bar(
                            loaded, 
                            len(loaded_queue)
                        )
                        await loading_msg.edit(embeds=[embed])

                embed.description = util.progress_bar(
                    loaded, 
                    len(loaded_queue)
                )

                logging.info(f"New queue loaded! ID: '{name}'")
                await ctx.send(f"Queue '{name}' loaded! :tada:")
                return
        else:
            logging.warn(f"Something went wrong! A queue was requested but no name given.")
            await ctx.send(f"Not sure how you managed to get around the required 'name' field but please contact <@278441913361629195> ASAP.")

def setup(bot):
    bot.add_cog(Load(bot))