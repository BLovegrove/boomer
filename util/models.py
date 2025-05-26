import discord
from discord.ext import commands
import lavalink
from lavalink.errors import ClientError
from loguru import logger

from util.handlers import extensions
import util.config as cfg


class LavaBot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            intents=discord.Intents.all(), command_prefix=commands.when_mentioned
        )
        self.command_list = extensions.search(extensions.Type.COMMAND)
        self.event_list = extensions.search(extensions.Type.EVENT)
        self.task_list = extensions.search(extensions.Type.TASK)

        self.lavalink: lavalink.Client = None
        self.player_exists = False

    def update_lavalink(self):
        self.lavalink = lavalink.Client(self.user.id)

        self.lavalink.add_node(
            host=cfg.lavalink.host,
            port=cfg.lavalink.port,
            password=cfg.lavalink.password,
            name=cfg.lavalink.label,
            region="au",
        )

        for cog in self.cogs.values():
            self.lavalink.add_event_hooks(cog)

    # load cogs
    async def setup_hook(self) -> None:
        for command in self.command_list:
            await self.load_extension(command)

        for event in self.event_list:
            await self.load_extension(event)

        for task in self.task_list:
            await self.load_extension(task)

        logger.debug("Finished loading setup_hook")

        return await super().setup_hook()


class LavalinkVoiceClient(discord.VoiceProtocol):
    def __init__(self, client: discord.Client, channel: discord.VoiceChannel):
        self.client = client
        self.channel: discord.VoiceChannel = channel
        self._destroyed = False

        if hasattr(self.client, "lavalink"):
            self.lavalink: lavalink.Client = self.client.lavalink
        else:
            self.client.lavalink = lavalink.Client(client.user.id)
            self.client.lavalink.add_node(
                cfg.lavalink.host,
                cfg.lavalink.port,
                cfg.lavalink.password,
                "us",
                "default-node",
            )
            self.lavalink: lavalink.Client = self.client.lavalink

    async def on_voice_server_update(self, data):
        # the data needs to be transformed before being handed down to
        # voice_update_handler
        lavalink_data = {"t": "VOICE_SERVER_UPDATE", "d": data}
        await self.lavalink.voice_update_handler(lavalink_data)

    async def on_voice_state_update(self, data):
        channel_id = data["channel_id"]

        if not channel_id:
            await self._destroy()
            return

        self.channel = self.client.get_channel(int(channel_id))

        # the data needs to be transformed before being handed down to
        # voice_update_handler
        lavalink_data = {"t": "VOICE_STATE_UPDATE", "d": data}

        await self.lavalink.voice_update_handler(lavalink_data)

    async def connect(
        self,
        *,
        timeout: float,
        reconnect: bool,
        self_deaf: bool = False,
        self_mute: bool = False,
    ) -> None:
        """
        Connect the bot to the voice channel and create a player_manager
        if it doesn't exist yet.
        """
        # ensure there is a player_manager when creating a new voice_client
        self.lavalink.player_manager.create(self.channel.guild.id)
        await self.channel.guild.change_voice_state(
            channel=self.channel, self_mute=self_mute, self_deaf=self_deaf
        )

    async def disconnect(self, force: bool = False) -> None:
        """
        Handles the disconnect.
        Cleans up running player and leaves the voice client.
        """
        player = self.lavalink.player_manager.get(self.channel.guild.id)

        # no need to disconnect if we are not connected
        if not force and not player.is_connected:
            return

        # None means disconnect
        await self.channel.guild.change_voice_state(channel=None)

        # update the channel_id of the player to None
        # this must be done because the on_voice_state_update that would set channel_id
        # to None doesn't get dispatched after the disconnect
        player.channel_id = None
        await self._destroy()

    async def _destroy(self):
        self.cleanup()

        if self._destroyed:
            # Idempotency handling, if `disconnect()` is called, the changed voice state
            # could cause this to run a second time.
            return

        self._destroyed = True

        try:
            await self.lavalink.player_manager.destroy(self.channel.guild.id)
        except ClientError:
            pass
