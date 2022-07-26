import { SlashCommandBuilder } from "@discordjs/builders";
import { CommandInteraction } from "discord.js";
import { Player } from "erela.js";
import { VoiceHelper } from "../../util/helpers";
import { MusicHelper } from "../../util/helpers/music";
import { Boomer, Command } from "../../util/structures";

export const command: Command = {
    data: new SlashCommandBuilder()
        .setName("skip")
        .setDescription("Skips next song in queue by default.")
        .addNumberOption(option =>
            option.setName("index")
            .setDescription('The number in the queue you want to skip to')
            .setRequired(true) )
        ,
    async execute(interaction: CommandInteraction, client: Boomer) {
        const MH = new MusicHelper(client)

        const index = interaction.options.getNumber('index', true)
        await MH.skip(interaction,index)
    }
}