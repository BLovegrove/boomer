import { SlashCommandBuilder } from "@discordjs/builders";
import { CommandInteraction, GuildMemberRoleManager } from "discord.js";
import { MusicHandler } from "../../util/handlers";
import { ExtendedClient, Command } from "../../util/structures";
import fetch from "cross-fetch"
import cfg from "../../config.json"
import Favs from "../../util/models/favs";

export const command: Command = {
    data: new SlashCommandBuilder()
        .setName("favs")
        .setDescription("Queue up some of your favorite tunes!")
        .addSubcommand(command => 
			command
				.setName("list")
				.setDescription("Show a list of all the favorites for your group. Play them from the list directly!")
		)
        ,
    async execute(interaction: CommandInteraction, client: ExtendedClient) {

		if (interaction.options.getSubcommand() == "list") {
			// send message here

			await interaction.deferReply({ephemeral: true})
			var favs = null

			// Checks each role for a favs list. Grabs the first one it finds
			const memberRoleManager = interaction.member!.roles as GuildMemberRoleManager
			const memberRoles = Array.from(memberRoleManager.cache.keys())
			for (const role of memberRoles) {
				const response = await fetch(cfg.db.requestURL + "/favs/role/" + role)
				console.log(response.status)
				if (response.ok) {
					favs = await response.json()
					break
				}
			}

			// Kills command if no favs list was found
			if (!favs) {
				await interaction.editReply({
					content: "None of your roles support a favs list! If you think this is a mistake, ping your friendly neighborhood admin."
				})

				return
			}

			await interaction.editReply("List found!")
			// interaction.followUp(favs)
		}
    }
}