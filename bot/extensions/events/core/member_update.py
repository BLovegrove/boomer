import discord
from discord.ext import commands
from loguru import logger

from util import models

from util.handlers.database import DatabaseHandler


class MemberUpdate(commands.Cog):
    def __init__(self, bot: models.LavaBot) -> None:
        self.bot = bot
        self.db = DatabaseHandler(self.bot.db)

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):

        logger.debug(f"Member updated: {before.name}")

        details_update = self.db.update_member(
            member = after,
            name_changed = before.display_name != after.display_name,
            avatar_changed = before.display_avatar.key != after.display_avatar.key,
            roles_changed = before.roles != after.roles,
        )

        if details_update:
            logger.info(
                f"Member '{after.display_name}' Updated:"
                + f"| Details {"✅" if details_update else "❌"}"
            )

        else:
            logger.debug("Member update did not execute - no changes detected")


async def setup(bot):
    await bot.add_cog(MemberUpdate(bot))
