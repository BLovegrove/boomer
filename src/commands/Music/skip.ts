import { SlashCommandBuilder } from "@discordjs/builders";
import { CommandInteraction } from "discord.js";
import { MusicHandler } from "../../util/handlers/music";
import { ExtendedClient, Command } from "../../util/structures";

export const command: Command = {
    data: new SlashCommandBuilder()
        .setName("skip")
        .setDescription("Skips next song in queue by default.")
        .addNumberOption(option =>
            option
                .setName("index")
                .setDescription('The number in the queue you want to skip to')
        )
        ,
    async execute(interaction: CommandInteraction, client: ExtendedClient) {
        const MH = new MusicHandler(client)

        var index = interaction.options.getNumber('index')

        await MH.skip(interaction, (index === null ? 1 : index))
    }
}