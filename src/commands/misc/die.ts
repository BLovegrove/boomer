import { SlashCommandBuilder } from "@discordjs/builders";
import { CommandInteraction } from "discord.js";
import { Boomer, Command } from "../../util/structures";

export const command: Command = {
    data: new SlashCommandBuilder()
        .setName("die")
        .setDescription("Kills boomer. Restart him in the NYI web portal."),
    async execute(interaction: CommandInteraction, client: Boomer) {
        return interaction.reply("My battery is low and it's getting dark :(")
    }
}