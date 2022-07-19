import { SlashCommandBuilder } from "discord.js";
import { Command } from "../../types";

export const command: Command = {
    data: new SlashCommandBuilder()
        .setName("ping")
        .setDescription("Replies with Pong!"),
    async execute(interaction, client) {
        return interaction.reply("Pong!")
    }
}