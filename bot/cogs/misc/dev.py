import logging

import nextcord
from nextcord import slash_command
from nextcord.ext import commands

import config as cfg


class Dev(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @slash_command(
        name="dev",
        description=f"A series of developer commands for {cfg.bot.name}. BE CAREFUL WITH THESE.",
        guild_ids=[cfg.bot.guild_id],
    )
    @commands.has_role(1001722386976084071)
    async def dev(
        self,
        interaction: nextcord.Interaction,
        subcode: str = nextcord.SlashOption(
            name="subcommand",
            description="Runs a series of dev actions without cluttering the commands list.",
            choices={
                "Kill bot": "die",
                "Ping test": "ping",
                "Log Search Example": "searchex",
                "Log queue entries": "logqueue",
                "Log player state": "logplayer",
            },
            required=True,
        ),
    ):
        await interaction.response.defer(ephemeral=True)

        match (subcode):
            case "die":
                # disconnect voice

                await interaction.followup.send(
                    content=f"Success! {cfg.bot.name} now rebooting. Wait until they're online again before running more commands.",
                    ephemeral=False,
                )

                if cfg.dev.deregister_on_close:
                    logging.info("Deregistering commands...")
                    commands = self.bot.get_all_application_commands()
                    for command in commands:
                        await self.bot.delete_application_commands(
                            command, guild_id=cfg.bot.guild_id
                        )

                await self.bot.close()
                return

            case "ping":
                await interaction.followup.send(f"Pong! ({self.bot.pin}ms)")

                return


def setup(bot):
    bot.add_cog(Dev(bot))
