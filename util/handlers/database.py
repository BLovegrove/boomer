import discord
import util.config as cfg
from util.handlers import download
from util.models import BotDB


def update_member(
    db: BotDB,
    member: discord.Member,
    name_changed: bool = False,
    avatar_changed: bool = False,
    manual_trigger: bool = False,
    commit: bool = True,
):

    if not (name_changed or avatar_changed or manual_trigger):
        return False

    existing_member = db.execute(
        f"SELECT id FROM {cfg.db.table.members} WHERE id = {member.id}"
    )

    changes = {}

    if name_changed:
        changes["display_name"] = member.display_name

    if avatar_changed:
        changes["display_avatar"] = download.discord.pfp(
            member.display_avatar.url, commit
        )

    activity = discord.utils.get(member.activities, type=discord.ActivityType.custom)
    changes["status"] = "NULL" if not activity else activity.name
    if changes["status"] == "":
        changes["status"] == "NULL"

    if existing_member and (name_changed or avatar_changed or not commit):
        where = {"id": member.id}

        response = db.update(cfg.db.table.members, changes, where, commit)
        return True if commit else response

    elif not existing_member:
        changes["id"] = member.id
        changes["display_name"] = member.display_name
        changes["display_avatar"] = download.discord.pfp(
            member.display_avatar.url, commit
        )

        response = db.insert(cfg.db.table.members, changes, commit)
        return True if commit else response

    else:
        return False
