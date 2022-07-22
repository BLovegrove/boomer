import { SlashCommandBuilder } from "@discordjs/builders";
import { Command } from "../../structures";

export const command: Command = {
    data: new SlashCommandBuilder()
        .setName("ping")
        .setDescription("Replies with Pong!"),
    async execute(interaction, client) {
        return interaction.reply("Pong!")
    }
}