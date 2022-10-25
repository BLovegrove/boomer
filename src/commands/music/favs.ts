import { SlashCommandBuilder } from "@discordjs/builders";
import { CommandInteraction } from "discord.js";
import { MusicHandler } from "../../util/handlers";
import { ExtendedClient, Command } from "../../util/structures";

export const command: Command = {
    data: new SlashCommandBuilder()
        .setName("favs")
        .setDescription("Queue up some of your favorite tunes. Ping your local bot devs to add more!")
        .addStringOption(option =>
            option
                .setName("song")
                .setDescription("The favorite tune you want to play.")
                .setRequired(true)
        )
        ,
    async execute(interaction: CommandInteraction, client: ExtendedClient) {
        const songURL = interaction.options.getString('song', true)

        const MH = new MusicHandler(client)

        await MH.play(interaction, songURL)
    }
}