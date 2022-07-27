import { SlashCommandBuilder } from "@discordjs/builders";
import { CommandInteraction } from "discord.js";
import { MusicHelper } from "../../util/helpers/music";
import { Boomer, Command } from "../../util/structures";

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
    async execute(interaction: CommandInteraction, client: Boomer) {
        const MH = new MusicHelper(client)

        var index = interaction.options.getNumber('index')

        await MH.skip(interaction, (index === null ? 0 : index))
    }
}