import discord
from loguru import logger

from util import cfg, models
from util.handlers import download as DownloadHandler

__all__ = ["DatabaseHandler"]


def _get_heirarchy(member: discord.Member):
    logger.debug(f"Role heirarchy is: {cfg.role.heirarchy}")
    id = None
    for role_id in cfg.role.heirarchy:
        if member.guild.get_role(int(role_id)) in member.roles:
            id = role_id
            break

    return id


class DatabaseHandler:
    def __init__(self, db: models.BotDB):
        self.db: models.BotDB = db

    def update_member(
        self,
        member: discord.Member,
        name_changed: bool = False,
        avatar_changed: bool = False,
        manual_trigger: bool = False,
        commit: bool = True,
    ):

        if not (name_changed or avatar_changed or manual_trigger):
            return False

        existing_member = self.db.execute(
            f"SELECT id FROM {cfg.db.table.members} WHERE id = {member.id}"
        )

        changes = {}

        if name_changed:
            changes["display_name"] = member.display_name

        if avatar_changed:
            changes["display_avatar"] = DownloadHandler.Discord.pfp(
                member.display_avatar.url, commit
            )

        activity = discord.utils.get(
            member.activities, type=discord.ActivityType.custom
        )
        changes["status"] = "NULL" if not activity else activity.name
        if changes["status"] == "":
            changes["status"] == "NULL"

        if existing_member and (name_changed or avatar_changed or not commit):
            where = {"id": member.id}

            response = self.db.update(cfg.db.table.members, changes, where, commit)
            return True if commit else response

        elif not existing_member:
            changes["id"] = member.id
            changes["display_name"] = member.display_name
            changes["display_avatar"] = DownloadHandler.Discord.pfp(
                member.display_avatar.url, commit
            )

            response = self.db.insert(cfg.db.table.members, changes, commit)
            return True if commit else response

        else:
            return False

    def get_favorites(self, member: discord.Member):

        id = member.id
        query = f"SELECT * FROM {cfg.db.table.favs} WHERE owner_id='{id}'"
        fav = self.db.execute(query)

        if not fav:
            heirarchy = _get_heirarchy(member)
            id = heirarchy if heirarchy else id
            fav = self.db.execute(query)

        if not fav:
            id = "!DEFAULT"
            fav = self.db.execute(query)

        return fav if fav else None

    def get_bgm(self, member: discord.Member):

        role_id = _get_heirarchy(member)
        if not role_id:
            return cfg.player.bgm_default

        bgm = self.db.execute(
            f"SELECT url FROM {cfg.db.table.bgm} WHERE role_id={role_id}"
        )

        if not bgm:
            return False

        return bgm["url"]

    def set_bgm(self, member: discord.Member, url: str, commit: bool = True):

        role_id = _get_heirarchy(member)

        bgm = self.get_bgm(member)
        logger.debug(bgm)

        if not bgm:
            result = self.db.insert(
                cfg.db.table.bgm,
                {"role_id": role_id, "url": url},
                commit,
            )
            logger.debug(result)
        else:
            result = self.db.update(
                cfg.db.table.bgm, {"url": url}, {"role_id": role_id}, commit
            )
            logger.debug(result)

        return True
