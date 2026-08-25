import discord
from loguru import logger

from util import cfg, models
from util.handlers.download import DownloadHandler

__all__ = ["DatabaseHandler"]


def _get_heirarchy(member: discord.Member, db: models.BotDB):
    query = f"SELECT hierarchy FROM {cfg.db.table.members} WHERE id={member.id}"
    id = db.execute(query, fetchone=True)
    return id


class DatabaseHandler:
    def __init__(self, db: models.BotDB):
        self.db: models.BotDB = db

    def update_member(
        self,
        member: discord.Member,
        name_changed: bool = False,
        avatar_changed: bool = False,
        roles_changed: bool = False,
        manual_trigger: bool = False,
        commit: bool = True,
    ):

        if not (name_changed or avatar_changed or roles_changed or manual_trigger):
            return False

        existing_member = self.db.execute(
            f"SELECT id FROM {cfg.db.table.members} WHERE id = `{member.id}`"
        )

        changes = {}

        if name_changed or manual_trigger:
            changes["display_name"] = member.display_name

        if avatar_changed or manual_trigger:
            changes["display_avatar"] = DownloadHandler.Discord.pfp(
                member.display_avatar.url, commit
            )

        if roles_changed:
            logger.debug(f"Role heirarchy is: {cfg.role.heirarchy}")
            hierarchy_id = cfg.role.heirarchy[-1]
            for role_id in cfg.role.heirarchy:
                if member.guild.get_role(int(role_id)) in member.roles:
                    hierarchy_id = role_id
                    break

            changes["hierarchy"] = hierarchy_id

        activity = discord.utils.get(
            member.activities, type=discord.ActivityType.custom
        )
        changes["status"] = "NULL" if not activity else activity.name
        if changes["status"] == "":
            changes["status"] == "NULL"

        if existing_member and (
            name_changed or avatar_changed or not commit or manual_trigger
        ):
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

    def create_favorite(
        self,
        name: str,
        member: discord.Member,
        private: bool = True,
        shuffled: bool = False,
    ):
        changes = {
            "name": name,
            "owner_id": member.id,
            "role_id": _get_heirarchy(member, self.db),
            "entries": "{}",
            "private": private,
            "shuffled": shuffled,
        }

        is_duplicate = self.db.execute(
            f"SELECT * FROM {cfg.db.table.favs} WHERE name = %s LIMIT 1", [name]
        )
        if is_duplicate:
            logger.error(
                "SQL Error: User tried to make a favorites list with a non-unique ID."
            )
            return False
        else:
            response = self.db.insert(cfg.db.table.favs, changes)
            return True

    def get_favorites(self, member: discord.Member, private: bool = False):

        if private:
            query = f"SELECT name FROM {cfg.db.table.favs} WHERE owner_id={member.id}"
            favs = self.db.execute(query, fetchone=False)
        else:
            heirarchy = _get_heirarchy(member, self.db)
            query = f"SELECT name FROM {cfg.db.table.favs} WHERE owner_id={member.id} OR (role_id={heirarchy} AND private=0)"
            favs = self.db.execute(query, fetchone=False)

        list = []
        if favs:
            for item in favs:
                list.append(item["name"])

        return list if favs else None

    def get_favorites_byname(self, list_name: str):

        query = f"SELECT * FROM {cfg.db.table.favs} WHERE name=%s"
        fav = self.db.execute(query, [list_name])

        return fav if fav else None

    def update_favorites(
        self,
        list_name: str,
        new_favs: str = None,
        private: bool = None,
        shuffled: bool = None,
    ):

        if new_favs:
            result = self.db.update(
                cfg.db.table.favs, {"entries": new_favs}, {"name": list_name}
            )
            logger.debug(result)

        if private != None:
            result = self.db.update(
                cfg.db.table.favs, {"private": private}, {"name": list_name}
            )
            logger.debug(result)

        if shuffled != None:
            result = self.db.update(
                cfg.db.table.favs, {"shuffled": shuffled}, {"name": list_name}
            )
            logger.debug(result)

    def delete_favorites(self, list_name: str):

        query = f"DELETE FROM {cfg.db.table.favs} WHERE name=%s LIMIT 1"
        result = self.db.execute(query, [list_name], commit=True)

        return result

    def get_bgm(self, member: discord.Member):

        role_id = _get_heirarchy(member, self.db)
        if not role_id:
            return cfg.player.bgm_default

        bgm = self.db.execute(
            f"SELECT url FROM {cfg.db.table.bgm} WHERE owner_id={role_id}"
        )

        if not bgm:
            bgm = self.db.execute(
                f"SELECT url FROM {cfg.db.table.bgm} WHERE owner_id=!DEFAULT"
            )

        if not bgm:
            return
        else:
            return bgm["url"]

    def set_bgm(self, member: discord.Member, url: str, commit: bool = True):

        role_id = _get_heirarchy(member, self.db)

        bgm = self.db.execute(
            f"SELECT url FROM `{cfg.db.table.bgm}` WHERE owner_id={role_id}"
        )
        logger.debug(bgm)

        if not bgm:
            result = self.db.insert(
                cfg.db.table.bgm,
                {"owner_id": role_id, "url": url},
                commit,
            )
            logger.debug(result)
        else:
            result = self.db.update(
                cfg.db.table.bgm, {"url": url}, {"owner_id": role_id}, commit
            )
            logger.debug(result)

        return True
