import { SlashCommandBuilder } from "@discordjs/builders";
import { CommandInteraction } from "discord.js";
import { MusicHandler } from "../../util/handlers";
import { ExtendedClient, Command } from "../../util/structures";

export const command: Command = {
    data: new SlashCommandBuilder()
        .setName("play")
        .setDescription("Plays music! Summons boomer if he isn't running, adds a song to the queue if he is.")
        .addStringOption(option => option
            .setName('search')
            .setDescription('The name/artist/url of the song you want to find')
            .setRequired(true)
        )
        ,
    async execute(interaction: CommandInteraction, client: ExtendedClient) {
        const MH = new MusicHandler(client)

        const searchString = interaction.options.getString('search', true)
        await MH.play(interaction, searchString)
    }
}