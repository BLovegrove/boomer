import { SlashCommandBuilder } from "@discordjs/builders";
import { CommandInteraction } from "discord.js";
import { VoiceHandler } from "../../util/handlers";
import { ExtendedClient, Command } from "../../util/structures";

export const command: Command = {
    data: new SlashCommandBuilder()
        .setName("repeat")
        .setDescription("Starts looping either the current track, or the entire playlist.")
		.addStringOption(option => option
			.setName("mode")
			.setDescription("Pick between track and entire playlist to enable repeating on.")
			.addChoices(
				{name: "track", value: "track"},
				{name: "playlist", value: "playlist"},
			)
			.setRequired(true)
		)
        ,
    async execute(interaction: CommandInteraction, client: ExtendedClient) {

		const VH = new VoiceHandler(client)
		const player = await VH.ensureVoice(interaction)
		if (!player) {
			return
		}

		if (!player.playing || player.get("idle")) {
			await interaction.reply({content: "Idlinng / Nothing playing at the moment. Try queueing up something first.", ephemeral: true})
			return
		}

		const option = interaction.options.getString("mode", true)

		switch(option) {
			case "track": {
				player.setQueueRepeat(false)
				player.setTrackRepeat(true)

				await interaction.reply("Looping on track :repeat_one:")
				return
			}
			case "playlist": {
				player.setQueueRepeat(true)
				player.setTrackRepeat(false)

				await interaction.reply("Looping on playlist :repeat:")
				return
			}
		}

        return
    }
}