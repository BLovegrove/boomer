import { SlashCommandBuilder } from "@discordjs/builders";
import { Command } from "../../structures";

export const command: Command = {
    data: new SlashCommandBuilder()
        .setName("die")
        .setDescription("Kills boomer. Restart him in the NYI web portal."),
    async execute(interaction, client) {
        return interaction.reply("My battery is low and it's getting dark :(")
    }
}