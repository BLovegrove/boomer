import { SlashCommandBuilder } from "@discordjs/builders";
import { CommandInteraction } from "discord.js";
import { MusicHelper } from "../../util/helpers";
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
                .addChoices(
                    { name: "Doom OST", value: "https://www.youtube.com/watch?v=Jm932Sqwf5E"},
                    { name: "Bluegrass Banjo", value: "https://www.youtube.com/watch?v=85mDyWCgHy0"},
                    { name: "Coconut Mall", value: "https://www.youtube.com/watch?v=cscuCIzItZQ"},
                    { name: "Crab Rave", value: "https://www.youtube.com/watch?v=mRq_Kldhh28"},
                    { name: "Rickroll", value: "https://www.youtube.com/watch?v=dQw4w9WgXcQ"},
                    { name: "Earthbound", value: "https://www.youtube.com/watch?v=6M-NkQAo-3E&t=1s"},
                    { name: "Roooocks", value: "https://www.youtube.com/watch?v=GInovXm59Ew"}
                )
        )
        ,
    async execute(interaction: CommandInteraction, client: ExtendedClient) {
        const songURL = interaction.options.getString('song', true)

        const MH = new MusicHelper(client)
        await MH.play(interaction, songURL)
    }
}