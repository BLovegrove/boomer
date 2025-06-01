import logging
import discord
from discord.ext import commands
import lavalink
from lavalink.errors import ClientError
from loguru import logger
import mysql.connector as mysqlconn
import mysql.connector.cursor as mysqlcurs
import mysql.connector.pooling as mysqlpool

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
        self.db = BotDB()

    def update_lavalink(self):
        self.lavalink = lavalink.Client(self.user.id)

        self.lavalink.add_node(
            host=cfg.lavalink.host,
            port=cfg.lavalink.port,
            password=cfg.lavalink.password,
            name=cfg.lavalink.label,
            region=cfg.lavalink.region,
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
        player: lavalink.player.DefaultPlayer = self.lavalink.player_manager.get(
            self.channel.guild.id
        )

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


# override MySQLconnectionPool because mysql python devs are fucking stupid and didnt type their fucking class properly (fuck you)
class MySQLConnectionLeanPool(mysqlpool.MySQLConnectionPool):
    def __init__(self, pool_size=5, pool_name=None, pool_reset_session=True, **kwargs):
        super().__init__(pool_size, pool_name, pool_reset_session, **kwargs)

    def get_connection(self) -> mysqlconn.MySQLConnection:
        return super().get_connection()


class BotDB:
    def __init__(self):

        logging.getLogger("mysql.connector").setLevel("FATAL")

        self.dbconfig = {
            "host": cfg.db.host,
            "user": cfg.db.user,
            "password": cfg.db.password,
            "database": cfg.db.name,
        }

        self.test_connection()
        self.pool = self.create_pool()

    def create_pool(self):

        pool = MySQLConnectionLeanPool(
            pool_name=cfg.db.pool,
            pool_reset_session=True,
            **self.dbconfig,
        )

        return pool

    def test_connection(self):
        try:
            connection = mysqlconn.connect(**self.dbconfig)
            logger.success(
                f"Database {cfg.db.name}@{cfg.db.host} connection established"
            )

            if cfg.log_level == "DEBUG":
                logger.debug("Debug Mode active. DB commits will be blocked")

            connection.close()
            return True

        except mysqlconn.Error as e:
            logger.error(e)
            return False

    def execute(
        self,
        query: str,
        args: tuple = None,
        commit: bool = False,
        fetchone: bool = True,
    ):
        """Executes query string. Commits changes if commit = true, otherwise returns result of fetchall()

        Args:
            query (str): SQL query string. If using palceholdes, don't forget to add args.
            args (tuple, optional): SQL-compatible arguments for query string placeholders. Defaults to None.
            commit (bool, optional): Whether or not commit query changes to the DB. Defaults to False.
            fetch (bool, optional): Whether to fetch one or fetch many if commit = false. Defaults to True

        Returns:
            _type_: _description_
        """
        if args and len(args) != query.count("%"):
            logger.error(
                f"Attempted to execute query with mismatched arguments. # of values: {query.count("%")}, # of args: {len(args)}"
            )
            return None

        if cfg.log_level == "DEBUG":
            commit = False

        result = []

        with self.pool.get_connection() as connection:
            with connection.cursor(dictionary=True) as cursor:

                cursor.execute(query, args)

                if commit:
                    connection.commit()
                else:
                    result = cursor.fetchone() if fetchone else cursor.fetchall()

        return result

    def insert(self, table: str, changes: dict[str], commit: bool = True):

        columns = list(changes.keys())
        values = list(changes.values())

        query = (
            "INSERT INTO "
            + table
            + " ("
            + ",".join(columns)
            + ") VALUES ("
            + (",".join(["%s" for column in range(len(columns))]))
            + ")"
        )

        try:
            self.execute(query, tuple(values), commit)
        except mysqlconn.errors.ProgrammingError as e:
            logger.error(f"MySQL Error #{e.errno} while inserting row into {table}")
            logger.error(f"Query string: {query}")
            logger.error(f"Query args: {values}")

        return query % tuple(values)

    def update(
        self, table: str, changes: dict[str], where: dict[str], commit: bool = True
    ):

        columns = list(changes.keys())
        id_column = list(where.keys())[0]
        id_value = list(where.values())[0]

        query = (
            "UPDATE "
            + table
            + " SET "
            + ",".join([f"{column}=%s" for column in columns])
            + " WHERE "
            + id_column
            + "=%s"
        )

        values = tuple(list(changes.values()))
        values += (id_value,)

        try:
            self.execute(query, values, commit)
        except mysqlconn.errors.ProgrammingError as e:
            logger.error(
                f"MySQL Error #{e.errno} while updating row {id_value} in {table}"
            )
            logger.error(f"Query string: {query}")
            logger.error(f"Query args: {values}")

        return query % values

    def close(
        self,
        connection: mysqlconn.MySQLConnection,
        cursor: mysqlcurs.MySQLCursorDict,
    ):
        try:
            cursor.close()
            connection.close()
            return True
        except Exception as e:
            logger.error(e)
            return False
