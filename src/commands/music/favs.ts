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
                .addChoices(
                    { name: "Doom OST", value: "https://www.youtube.com/watch?v=Jm932Sqwf5E"},
                    { name: "Bluegrass Banjo", value: "https://www.youtube.com/watch?v=85mDyWCgHy0"},
                    { name: "Coconut Mall", value: "https://www.youtube.com/watch?v=cscuCIzItZQ"},
                    { name: "Crab Rave", value: "https://www.youtube.com/watch?v=mRq_Kldhh28"},
                    { name: "Rickroll", value: "https://www.youtube.com/watch?v=dQw4w9WgXcQ"},
                    { name: "Earthbound", value: "https://www.youtube.com/watch?v=6M-NkQAo-3E"},
                    { name: "Roooocks", value: "https://www.youtube.com/watch?v=ZPjSV-lnqvg"},
                    { name: "Country Calendar", value: "https://www.youtube.com/watch?v=p9i0O-G8Wa8"},
                    { name: "OuiOui", value: "https://www.youtube.com/watch?v=BFxZ15xXVRk"},
                    { name: "Pizzatime", value: "https://www.youtube.com/watch?v=czTksCF6X8Y"},
                    { name: "PIZZATIME 😂", value: "https://www.youtube.com/watch?v=lpvT-Fciu-4"},
                    { name: "BigEnough", value: "https://www.youtube.com/watch?v=rvrZJ5C_Nwg"},
                )
        )
        ,
    async execute(interaction: CommandInteraction, client: ExtendedClient) {
        const songURL = interaction.options.getString('song', true)

        const MH = new MusicHandler(client)
        await MH.play(interaction, songURL)
    }
}