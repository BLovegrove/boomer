import { SlashCommandBuilder } from "@discordjs/builders";
import { CommandInteraction } from "discord.js";
import { MusicHelper } from "../../util/helpers/music";
import { Boomer, Command } from "../../util/structures";

export const command: Command = {
    data: new SlashCommandBuilder()
        .setName("jump")
        .setDescription("Jumps to a song in queue without removing items. Default is jumping to the next song")
        .addNumberOption(option =>
            option
                .setName("index")
                .setDescription('The number in the queue you want to jump to')
        )
        ,
    async execute(interaction: CommandInteraction, client: Boomer) {
        const MH = new MusicHelper(client)

        var index = interaction.options.getNumber('index')

        await MH.skip(interaction, (index === null ? 1 : index), false)
    }
}