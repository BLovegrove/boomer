import { SlashCommandBuilder } from "@discordjs/builders";
import { CommandInteraction } from "discord.js";
import { VoiceHandler } from "../../util/handlers";
import { ExtendedClient, Command } from "../../util/structures";
import config from "../../config.json"
import fs from "fs"
import path from "path"

export const command: Command = {
    data: new SlashCommandBuilder()
        .setName("setbgm")
        .setDescription("Chages the background music.")
		.addStringOption(
			option => option
				.setName("track")
				.setDescription("Must be a valid YouTube URL for a single video. SoundCloud support coming soon.")
				.setRequired(true)
		)
        ,
    async execute(interaction: CommandInteraction, client: ExtendedClient) {

		const ytRegex = /(?:youtube\.com\/\S*(?:(?:\/e(?:mbed))?\/|watch\/?\?(?:\S*?&?v\=))|youtu\.be\/)([a-zA-Z0-9_-]{6,11})/g;
		const newTrack = interaction.options.getString("track", true).match(ytRegex)?.at(0)

		if (!newTrack || newTrack== "") {
			await interaction.reply("No valid YouTube URL detected. Try something else.")
			return
		}

		config.music.idleTrack = "https://www." + newTrack

		const newConfig = JSON.stringify(config, null, 1)

		const configDir = path.join(__dirname + "../../../config.json")

		fs.writeFileSync(configDir, newConfig)

		try { 
			const player = VoiceHandler.fetchPlayer(client)
			if (player.get("idle")) {
				player.manager.emit('queueEnd')
			}
		}
		catch (e) {
			console.log("No player found. Skipping idle track liveupdate.")
		}

		await interaction.reply("Success! New background music set.")
    }
}