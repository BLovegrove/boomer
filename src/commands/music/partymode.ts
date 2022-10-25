import { SlashCommandBuilder } from "@discordjs/builders";
import { CommandInteraction } from "discord.js";
import { VoiceHandler } from "../../util/handlers";
import { ExtendedClient, Command } from "../../util/structures";

export const command: Command = {
    data: new SlashCommandBuilder()
        .setName("partymode")
        .setDescription("Clears the queue, adds all your favorites, and enables 'queue-repeat'")
        ,
    async execute(interaction: CommandInteraction, client: ExtendedClient) {
        const VH = new VoiceHandler(client)
		const player = await VH.ensureVoice(interaction)
		if (!player) {
			return
		}
    }
}