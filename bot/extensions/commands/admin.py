# core imports
import discord
from discord.ext import commands
from discord import app_commands
from discord.app_commands import Choice
from loguru import logger

# custom imports
from util import cfg, models
from util.handlers.queue import QueueHandler
from util.handlers.voice import VoiceHandler
from util.handlers.music import MusicHandler
from util.handlers.database import DatabaseHandler


class Admin(commands.Cog):
    def __init__(self, bot: models.LavaBot) -> None:
        self.bot = bot
        self.voicehandler = VoiceHandler(bot)
        self.dbhandler = DatabaseHandler(self.bot.db)
        self.musichandler = MusicHandler(self.bot)
        self.queuehandler = QueueHandler(self.bot)

    @app_commands.command(
        name="admin",
        description=f"Runs a series of dev commands for testing and maintenance purposes.",
    )
    @app_commands.choices(
        command=[
            Choice(name="Kill bot", value="die"),
            Choice(name="Ping test", value="ping"),
            Choice(name="Fetch player info", value="fetchplayer"),
            Choice(name="Fill player queue", value="queuespam"),
            Choice(name="Register all members", value="forceregister"),
        ]
    )
    @commands.is_owner()
    async def admin(self, itr: discord.Interaction, command: Choice[str]):
        match command.value:
            case "die":
                await itr.response.send_message(
                    f"Restarting the bot. Please wait until {cfg.bot.name} has the 'Online' or 'Idle' status icon before doing any more commands.",
                    ephemeral=True,
                )
                # self.bot.tree.clear_commands(guild=itr.guild)
                # await self.bot.tree.sync(guild=itr.guild)
                # logger.info(f"Cleared all commands.")

                await self.bot.change_presence(status=discord.Status.offline)
                await self.bot.lavalink.close()
                await self.bot.close()
                return

            case "ping":
                await itr.response.send_message(
                    f"Pong! Here are the round trip times: \n"
                    + f"Bot: {round(self.bot.latency * 1000)}ms",
                    ephemeral=True,
                )
                return
            case "fetchplayer":
                await itr.response.defer(ephemeral=True)

                response = self.voicehandler.fetch_player(self.bot)
                if response.player:
                    player = response.player
                    player_data = [
                        f"- Name: {player.node.name}",
                        f"- Guild ID: {player.guild_id}",
                        f"- VC: <#{player.channel_id}>",
                        f"- Now playing: {player.current.title}",
                        f"- Queue length: {len(player.queue)}",
                        f"- Current Volume: {player.volume}",
                    ]
                else:
                    player_data = ["PLAYER NOT FOUND"]

                await itr.followup.send(
                    f"Player info:\n{"\n".join(player_data)}",
                    ephemeral=True,
                )
                return

            case "queuespam":
                await itr.response.send_message(
                    f"{cfg.player.loading_emoji} Spamming tons of entires to fill up the queue...",
                    ephemeral=True,
                )
                response = self.voicehandler

                songs = [
                    "https://www.youtube.com/watch?v=YnwfTHpnGLY",
                    "https://www.youtube.com/watch?v=tKi9Z-f6qX4",
                    "https://www.youtube.com/watch?v=B7xai5u_tnk",
                    "https://www.youtube.com/watch?v=n8X9_MgEdCg",
                    "https://www.youtube.com/watch?v=CqnU_sJ8V-E",
                ]

                result = await self.musichandler.play(response, songs)

                logger.debug("Spammed queue entries.")
                response.store("idle", False)
                response.set_loop(response.LOOP_NONE)
                await response.play()
                self.queuehandler.update_pages(response)
                await itr.edit_original_response(
                    content=f"{len(response.queue)} entries added to the queue. Now playing: {response.current.title}"
                )

            case "forceregister":
                await itr.response.send_message(
                    f"Forcing registration of all {len(itr.guild.members)} guild members...",
                    ephemeral=True,
                )

                for member in itr.guild.members:
                    self.dbhandler.update_member(member, manual_trigger=True)

                    logger.info(
                        f"Member [{str(itr.guild.members.index(member) + 1).zfill(len(str(len(itr.guild.members))))}/{len(itr.guild.members)}] Registered '{member.display_name}'"
                    )

                return

            case "default":
                await itr.response.send_message(
                    "Dev comamnd failed. Couldn't find a subcommand matching your input.",
                    ephemeral=True,
                )


async def setup(bot: models.LavaBot):
    await bot.add_cog(Admin(bot))
