# core imports
import json
from typing import List
import discord
from discord.ext import commands
from discord import app_commands
from discord.app_commands import Choice
from discord.utils import MISSING
import lavalink
from loguru import logger

# custom imports
from util import models
from util.handlers.music import MusicHandler
from util.handlers.voice import VoiceHandler
from util.handlers.embed import EmbedHandler
from util.handlers.database import DatabaseHandler


class Modals:
    class Favslist:
        class Add(discord.ui.Modal):
            def __init__(
                self,
                list_name: str,
                dbhandler: DatabaseHandler,
                musichandler: MusicHandler,
                bot: models.LavaBot,
            ):
                self.list_name = list_name
                self.dbhandler = dbhandler
                self.musichandler = musichandler
                self.bot = bot
                super().__init__(title=f"{list_name}: Add Track")

            track_url = discord.ui.Label(
                text="Track URL",
                component=discord.ui.TextInput(placeholder="Must start with https://"),
            )

            async def on_submit(self, itr: discord.Interaction):

                response: str = self.track_url.component.value
                if not response.startswith("https://"):
                    await itr.response.send_message(
                        f"Error! '{response}' was not a recognised URL. Try again",
                        ephemeral=True,
                    )
                    return

                list_entries: dict[str, str] = json.loads(
                    self.dbhandler.get_favorites_byname(self.list_name)["entries"]
                )
                urls = list_entries.values()
                if response in urls:
                    await itr.response.send_message(
                        f"Error! '{response}' is already in the facorites list. Try another",
                        ephemeral=True,
                    )
                    return

                track_info = await self.musichandler.load_tracks(
                    self.bot.lavalink.player_manager.create(itr.guild.id), response
                )
                if not track_info:
                    await itr.response.send_message(
                        f"Error! Failed to find info for '{response}'. Source might be down/URL Incorrect",
                        ephemeral=True,
                    )
                    return

                list_entries[track_info.title] = track_info.tracks[0].uri
                self.dbhandler.update_favorites(
                    self.list_name, json.dumps(list_entries)
                )
                await itr.response.send_message(
                    f"Success! '{track_info.title}' added to '{self.list_name}'",
                    ephemeral=True,
                )

                return await super().on_submit(itr)

        class Remove(discord.ui.Modal):
            def __init__(
                self,
                list_name: str,
                dbhandler: DatabaseHandler,
            ):

                self.list_name = list_name
                self.dbhandler = dbhandler

                self.list_entries: dict[str, str] = json.loads(
                    self.dbhandler.get_favorites_byname(self.list_name)["entries"]
                )

                self.track_select.component.options = [
                    discord.SelectOption(label=name, value=name)
                    for name in self.list_entries.keys()
                ]

                super().__init__(title=f"{list_name}: Remove Track")

            track_select = discord.ui.Label(
                text="Track URL",
                component=discord.ui.Select(),
            )

            async def on_submit(self, itr: discord.Interaction):

                response: str = self.track_select.component.values[0]

                self.list_entries.pop(response)

                self.dbhandler.update_favorites(
                    self.list_name, json.dumps(self.list_entries)
                )
                await itr.response.send_message(
                    f"Success! '{response}' removed from '{self.list_name}'",
                    ephemeral=True,
                )

                return await super().on_submit(itr)

        class EditFlags(discord.ui.Modal):
            def __init__(
                self,
                list_name: str,
                dbhandler: DatabaseHandler,
            ):

                self.list_name = list_name
                self.dbhandler = dbhandler

                self.list_items = self.dbhandler.get_favorites_byname(list_name)

                private = bool(self.list_items["private"])
                shuffled = bool(self.list_items["shuffled"])

                self.private_input.component.options = [
                    discord.SelectOption(label="True", value="true", default=private),
                    discord.SelectOption(
                        label="False", value="false", default=not private
                    ),
                ]

                self.shuffled_input.component.options = [
                    discord.SelectOption(label="True", value="true", default=shuffled),
                    discord.SelectOption(
                        label="False", value="false", default=not shuffled
                    ),
                ]

                super().__init__(title=f"{list_name}: Manage Settings Flags")

            private_input = discord.ui.Label(
                text="Private?",
                component=discord.ui.Select(),
            )

            shuffled_input = discord.ui.Label(
                text="Shuffled?",
                component=discord.ui.Select(),
            )

            async def on_submit(self, itr: discord.Interaction):

                is_private = (
                    True if self.private_input.component.values[0] == "true" else False
                )
                is_shuffled = (
                    True if self.shuffled_input.component.values[0] == "true" else False
                )

                self.dbhandler.update_favorites(
                    self.list_name, private=is_private, shuffled=is_shuffled
                )

                await itr.response.send_message(
                    f"Success! '{self.list_name}' is now {'private' if is_private else 'collaborative'} and {'shuffled' if is_shuffled else 'un-shuffled'}",
                    ephemeral=True,
                )

                return await super().on_submit(itr)

        class Nuke(discord.ui.Modal):
            def __init__(
                self,
                list_name: str,
                dbhandler: DatabaseHandler,
            ):

                self.list_name = list_name
                self.dbhandler = dbhandler

                self.disclaimer.content = (
                    f"Are you sure you want to delete '{self.list_name}'?"
                )

                super().__init__(title=f"Confirm Nuclear Option")

            disclaimer = discord.ui.TextDisplay(content="")

            confirm_nuke = discord.ui.Label(
                text="Re-type list name and submit to delete it:",
                component=discord.ui.TextInput(placeholder="This cannot be undone!"),
            )

            async def on_submit(self, itr: discord.Interaction):

                response: str = self.confirm_nuke.component.value

                if response != self.list_name:
                    await itr.response.send_message(
                        "Error! You didnt type out the list name correctly. Aborting...",
                        ephemeral=True,
                    )
                    return

                self.dbhandler.delete_favorites(self.list_name)
                await itr.response.send_message(
                    f"Success! '{self.list_name}' permanently destroyed. This must be how Oppenheimer felt",
                    ephemeral=True,
                )

                return await super().on_submit(itr)


class Favs(commands.Cog):

    def __init__(self, bot: models.LavaBot) -> None:
        self.bot = bot
        self.dbhandler = DatabaseHandler(bot.db)
        self.musichandler = MusicHandler(bot)
        self.voicehandler = VoiceHandler(bot)

    group = app_commands.Group(
        name="favs", description="Play, view, and manage your favorite tunes!"
    )

    async def favslists_auto(
        self, itr: discord.Interaction, current: str
    ) -> List[app_commands.Choice[str]]:
        favslists = self.dbhandler.get_favorites(itr.user)

        if not favslists:
            favslists = []

        return [
            app_commands.Choice(name=favslist, value=favslist)
            for favslist in favslists
            if current.lower() in favslist.lower()
        ]

    async def favslists_auto_private(
        self, itr: discord.Interaction, current: str
    ) -> List[app_commands.Choice[str]]:
        favslists = self.dbhandler.get_favorites(itr.user, True)

        if not favslists:
            favslists = []

        return [
            app_commands.Choice(name=favslist, value=favslist)
            for favslist in favslists
            if current.lower() in favslist.lower()
        ]

    # adds a favslist to the queue TODO: Make the 'shuffled' flag functional using this command
    @group.command(
        name="play",
        description="Play a list of your favorite songs! start typing to narrow down your search.",
    )
    @app_commands.autocomplete(list_name=favslists_auto)
    async def play(self, itr: discord.Interaction, list_name: str):
        await itr.response.defer()

        response = await self.voicehandler.ensure_voice(itr)
        if not response.player:
            await itr.followup.send(response.message)
            return
        else:
            player = response.player

        favs = self.dbhandler.get_favorites_byname(list_name)
        if not favs:
            await itr.followup.send(
                "No favs list found. If you're seeing this please show your bot admin.",
                ephemeral=True,
            )
            return

        list_decoded: dict = json.loads(favs["entries"])
        list_links = list(list_decoded.values())

        queue_start = len(player.queue)

        result = await self.musichandler.play(player, list_links)

        # guard if no results come back
        if not result:
            embed = EmbedHandler.TrackLoadFailed(itr, list_decoded)
            await itr.followup.send(embed=embed.construct())
            return

        embed = EmbedHandler.Playlist(
            itr, result.tracks, favs["name"], player, queue_start
        )

        await itr.followup.send(embed=embed.construct())

        # Extra alert for missing tracks if only some come back
        if len(result.tracks) < len(list_links):
            missing_tracks = {}
            loaded_tracks = []
            for track in result.tracks:
                loaded_tracks.append(track.uri)

            for name, url in list_decoded.items():
                if url not in loaded_tracks:
                    missing_tracks[name] = url

            embed = EmbedHandler.TrackLoadFailed(itr, missing_tracks)
            await itr.followup.send(embed=embed.construct())

    # creates an empty list with a unique name
    @group.command(
        name="create",
        description="Create an empty favorites list. Max 30 character name",
    )
    async def create(self, itr: discord.Interaction, list_name: str):
        await itr.response.defer(ephemeral=True)

        if len(list_name) > 30:
            await itr.followup.send(
                "Sorry, favorites list names have a character limit of 30. Make sure your character count is < 30."
            )

        list_created = self.dbhandler.create_favorite(list_name, itr.user)

        if list_created:
            await itr.followup.send(
                f"Success! {list_name} has been added to the database. You can start adding tracks and managing its settings now."
            )
        else:
            await itr.followup.send(
                f"Oops! There's already a favorites list with the name '{list_name}'. Try something else"
            )

    # prints tabbed list of favslist
    @group.command(
        name="info",
        description="View a favorites list! Pulls the contents of your favorites list without queuing anything",
    )
    @app_commands.autocomplete(list_name=favslists_auto)
    async def info(self, itr: discord.Interaction, list_name: str):
        await itr.response.defer()

        list = self.dbhandler.get_favorites_byname(list_name)
        if not list:
            await itr.followup.send(f"No favs list called '{list_name}' found")
            return

        embed = EmbedHandler.Favs(self.bot, list)

        await itr.followup.send(embed=embed.construct())

    # sends an ephemeral message with a prompt to pick a song to delete for 'remove' and a text box to enter a URL for 'add'
    # if too hard, autocomplete option for which song to delete or if a new URL is presented, it adds it to the list (assuming no dupe)
    @group.command(
        name="manage",
        description="Manage your favorites lists",
    )
    @app_commands.choices(
        action=[
            Choice(name="Add song", value="add"),
            Choice(name="Remove song", value="remove"),
            Choice(name="Manage flags", value="flags"),
            Choice(name="Delete list", value="nuke"),
        ]
    )
    @app_commands.autocomplete(list_name=favslists_auto_private)
    async def manage(
        self, itr: discord.Interaction, list_name: str, action: Choice[str]
    ):
        favs_list = self.dbhandler.get_favorites_byname(list_name)

        # ensure list exists
        if not favs_list:
            await itr.response.send_message(
                f"Error! Couldn't find a list called '{list_name}'",
                ephemeral=True,
            )
            return

        # ensure sender is owner of list before executing
        if str(itr.user.id) != favs_list["owner_id"]:
            await itr.response.send_message(
                f"Reply of shame! You don't have access to '{list_name}'. Stop trying to mess with it. Alerting owner: <@{favs_list["owner_id"]}>"
            )
            return

        match action.value:
            case "add":
                # discord dropdowns are limited to 25 entries. yikes.
                if len(json.loads(favs_list["entries"])) > 24:
                    await itr.response.send_message(
                        f"Error! '{list_name}' already includes 25 tracks - the max allowed by Discord",
                        ephemeral=True,
                    )
                    return

                # send modal with text entry and submit button
                modal = Modals.Favslist.Add(
                    list_name, self.dbhandler, self.musichandler, self.bot
                )

                await itr.response.send_modal(modal)

                return
            case "remove":
                if len(json.loads(favs_list["entries"])) < 1:
                    await itr.response.send_message(
                        f"Error! '{list_name}' is already empty. Nothing to remove",
                        ephemeral=True,
                    )
                    return

                # send modal with dropdown containing song options
                modal = Modals.Favslist.Remove(list_name, self.dbhandler)

                await itr.response.send_modal(modal)

                return
            case "flags":
                # send modal with flag options prefilled with current values
                modal = Modals.Favslist.EditFlags(list_name, self.dbhandler)

                await itr.response.send_modal(modal)

                return
            case "nuke":
                # send modal with confirm dialogue for delete permanently action
                modal = Modals.Favslist.Nuke(list_name, self.dbhandler)

                await itr.response.send_modal(modal)

                return


async def setup(bot: models.LavaBot):
    await bot.add_cog(Favs(bot))
